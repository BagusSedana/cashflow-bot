"""Mini App backend (aiohttp).

Serves:
- `GET  /`              — the static Mini App page (`webapp/index.html`)
- `POST /api/config`    — public client config (block id, earn_per_ad, mock flag)
- `POST /api/me`        — current user balance / counters (auth via initData)
- `POST /api/claim_ad`  — grant reward after the user finished a rewarded ad

All POST endpoints validate the Telegram WebApp `initData` HMAC signature
against `TELEGRAM_BOT_TOKEN`. Calls without a valid signature are 401-rejected,
so a user can't fabricate rewards by hitting the endpoint from outside the
Mini App.

A future v0.2.x can add a server-to-server reward callback from Adsgram
(verifying their HMAC) and only credit the user after Adsgram confirms the
view, eliminating the trust placed in the client-side `claim_ad` call.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import logging
import urllib.parse
from pathlib import Path

from aiohttp import web

from .config import settings
from .db import SessionLocal
from .services.earning_service import grant_ad_reward
from .services.user_service import get_user_by_telegram_id

logger = logging.getLogger("cashflow-bot.webapp")

WEBAPP_DIR = Path(__file__).resolve().parent.parent / "webapp"


def _verify_init_data(init_data: str, bot_token: str) -> dict[str, str] | None:
    """Validate Telegram Mini App initData signature. Returns parsed dict or None."""
    if not init_data:
        return None
    try:
        parsed = dict(urllib.parse.parse_qsl(init_data, keep_blank_values=True))
        their_hash = parsed.pop("hash", "")
        if not their_hash:
            return None
        data_check_string = "\n".join(
            f"{k}={parsed[k]}" for k in sorted(parsed.keys())
        )
        secret_key = hmac.new(
            b"WebAppData", bot_token.encode(), hashlib.sha256
        ).digest()
        our_hash = hmac.new(
            secret_key, data_check_string.encode(), hashlib.sha256
        ).hexdigest()
        if not hmac.compare_digest(our_hash, their_hash):
            return None
        return parsed
    except Exception:  # pragma: no cover - defensive
        logger.exception("init_data verification crashed")
        return None


def _user_id_from_init_data(parsed: dict[str, str]) -> int | None:
    user_json = parsed.get("user")
    if not user_json:
        return None
    try:
        user = json.loads(user_json)
        return int(user.get("id")) if user.get("id") is not None else None
    except Exception:
        return None


async def _authed_user(request: web.Request) -> tuple[web.Response | None, int | None]:
    try:
        body = await request.json()
    except Exception:
        return web.json_response({"error": "invalid json"}, status=400), None
    init_data = body.get("initData") or ""
    parsed = _verify_init_data(init_data, settings.telegram_bot_token)
    if parsed is None:
        return web.json_response({"error": "unauthorized"}, status=401), None
    user_id = _user_id_from_init_data(parsed)
    if user_id is None:
        return web.json_response({"error": "no user"}, status=400), None
    return None, user_id


async def index(request: web.Request) -> web.Response:
    path = WEBAPP_DIR / "index.html"
    if not path.is_file():
        return web.Response(status=404, text="webapp/index.html not found")
    return web.FileResponse(path, headers={"cache-control": "no-store"})


async def api_config(request: web.Request) -> web.Response:
    return web.json_response(
        {
            "earn_per_ad": settings.earn_per_ad,
            "adsgram_block_id": settings.adsgram_block_id,
            "mock": not settings.adsgram_block_id,
            "brand": settings.brand_name,
        }
    )


async def api_me(request: web.Request) -> web.Response:
    err, tg_id = await _authed_user(request)
    if err is not None:
        return err
    assert tg_id is not None
    async with SessionLocal() as session:
        user = await get_user_by_telegram_id(session, tg_id)
        if user is None:
            return web.json_response({"error": "user not registered, /start dulu"}, status=404)
        return web.json_response(
            {
                "telegram_id": user.telegram_id,
                "balance": user.balance,
                "ads_watched": user.ads_watched,
                "earn_per_ad": settings.earn_per_ad,
            }
        )


async def api_claim_ad(request: web.Request) -> web.Response:
    err, tg_id = await _authed_user(request)
    if err is not None:
        return err
    assert tg_id is not None
    async with SessionLocal() as session:
        user = await get_user_by_telegram_id(session, tg_id)
        if user is None:
            return web.json_response({"error": "user not registered"}, status=404)
        if user.is_banned:
            return web.json_response({"error": "akun dinonaktifkan"}, status=403)
        amount = await grant_ad_reward(session, user)
        await session.commit()
        return web.json_response(
            {
                "amount": amount,
                "balance": user.balance,
                "ads_watched": user.ads_watched,
            }
        )


def build_app() -> web.Application:
    app = web.Application()
    app.router.add_get("/", index)
    app.router.add_get("/index.html", index)
    app.router.add_post("/api/config", api_config)
    app.router.add_post("/api/me", api_me)
    app.router.add_post("/api/claim_ad", api_claim_ad)
    return app


async def start_webapp() -> web.AppRunner:
    """Start the aiohttp Mini App server. Returns the runner so caller can clean up."""
    app = build_app()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, settings.webapp_host, settings.webapp_port)
    await site.start()
    logger.info(
        "Webapp ready on http://%s:%s (public URL: %s)",
        settings.webapp_host,
        settings.webapp_port,
        settings.webapp_url or "<not configured>",
    )
    return runner
