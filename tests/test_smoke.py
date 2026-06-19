"""Lightweight smoke tests — run with: python -m pytest tests/

These don't need a real Telegram token; they verify the in-memory DB layer
and core service logic.
"""
from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path
from types import SimpleNamespace

# Set required env vars BEFORE importing bot.* (config reads them at import time)
os.environ.setdefault("TELEGRAM_BOT_TOKEN", "0:dummy")
os.environ.setdefault("ADMIN_IDS", "1")
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from bot import db as dbmod  # noqa: E402
from bot.config import settings  # noqa: E402
from bot.db import EarnSource, SessionLocal, WithdrawStatus, init_db  # noqa: E402
from bot.services.earning_service import (  # noqa: E402
    cooldown_remaining,
    grant_ad_reward,
    grant_referral_signup_bonus,
)
from bot.services.user_service import (  # noqa: E402
    get_or_create_user,
    referral_stats,
)
from bot.services.withdraw_service import (  # noqa: E402
    WithdrawError,
    approve,
    create_request,
    mark_paid,
    reject,
)


def _tg(uid: int, name: str = "Tester") -> SimpleNamespace:
    return SimpleNamespace(
        id=uid, username=f"user{uid}", first_name=name, language_code="id"
    )


async def _setup() -> None:
    # Force fresh schema in this in-memory DB
    async with dbmod.engine.begin() as conn:
        await conn.run_sync(dbmod.Base.metadata.drop_all)
    await init_db()


def run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


def test_create_user_and_referral():
    async def _go():
        await _setup()
        async with SessionLocal() as session:
            referrer, created_r = await get_or_create_user(session, _tg(100, "Ref"))
            assert created_r is True

            new_user, created_n = await get_or_create_user(
                session, _tg(101, "New"), referrer_telegram_id=100
            )
            assert created_n is True
            assert new_user.referrer_id == referrer.id

            bonus = await grant_referral_signup_bonus(session, referrer, new_user)
            assert bonus == settings.referral_signup_bonus
            assert referrer.balance == settings.referral_signup_bonus

            count, total = await referral_stats(session, referrer)
            assert count == 1
            assert total == settings.referral_signup_bonus
            await session.commit()

    run(_go())


def test_ad_reward_and_referral_commission():
    async def _go():
        await _setup()
        async with SessionLocal() as session:
            referrer, _ = await get_or_create_user(session, _tg(200))
            user, _ = await get_or_create_user(
                session, _tg(201), referrer_telegram_id=200
            )
            await session.commit()

        async with SessionLocal() as session:
            user = await get_or_create_user(session, _tg(201))  # fetches existing
            user_obj = user[0]
            assert cooldown_remaining(user_obj) == 0
            amount = await grant_ad_reward(session, user_obj)
            assert amount == settings.earn_per_ad
            assert user_obj.balance == settings.earn_per_ad
            assert user_obj.ads_watched == 1
            await session.commit()

        async with SessionLocal() as session:
            referrer_data = await get_or_create_user(session, _tg(200))
            ref_obj = referrer_data[0]
            expected_commission = (
                settings.earn_per_ad * settings.referral_percent // 100
            )
            assert ref_obj.balance == expected_commission

    run(_go())


def test_withdraw_lifecycle_pay():
    async def _go():
        await _setup()
        async with SessionLocal() as session:
            user, _ = await get_or_create_user(session, _tg(300))
            user.balance = settings.min_withdraw + 1000
            user.total_earned = user.balance
            await session.commit()
            user_id = user.id

        # create
        async with SessionLocal() as session:
            user = await session.get(dbmod.User, user_id)
            req = await create_request(
                session, user, settings.min_withdraw, "DANA", "0812000", "Tester"
            )
            await session.commit()
            assert user.balance == 1000
            req_id = req.id

        # approve
        async with SessionLocal() as session:
            req = await session.get(dbmod.WithdrawRequest, req_id)
            await approve(session, req)
            await session.commit()
            assert req.status == WithdrawStatus.APPROVED.value

        # mark paid
        async with SessionLocal() as session:
            req = await session.get(dbmod.WithdrawRequest, req_id)
            await mark_paid(session, req)
            await session.commit()
            user = await session.get(dbmod.User, user_id)
            assert req.status == WithdrawStatus.PAID.value
            assert user.total_withdrawn == settings.min_withdraw

    run(_go())


def test_withdraw_reject_refunds_balance():
    async def _go():
        await _setup()
        async with SessionLocal() as session:
            user, _ = await get_or_create_user(session, _tg(400))
            user.balance = settings.min_withdraw
            await session.commit()
            user_id = user.id

        async with SessionLocal() as session:
            user = await session.get(dbmod.User, user_id)
            req = await create_request(
                session, user, settings.min_withdraw, "DANA", "0812", "X"
            )
            await session.commit()
            assert user.balance == 0
            req_id = req.id

        async with SessionLocal() as session:
            req = await session.get(dbmod.WithdrawRequest, req_id)
            await reject(session, req, "test reason")
            await session.commit()
            user = await session.get(dbmod.User, user_id)
            assert user.balance == settings.min_withdraw  # refunded
            assert req.status == WithdrawStatus.REJECTED.value

    run(_go())


def test_withdraw_below_min_rejected():
    async def _go():
        await _setup()
        async with SessionLocal() as session:
            user, _ = await get_or_create_user(session, _tg(500))
            user.balance = settings.min_withdraw
            await session.commit()
            try:
                await create_request(
                    session, user, settings.min_withdraw - 1, "DANA", "0812", "X"
                )
            except WithdrawError:
                pass
            else:
                raise AssertionError("Expected WithdrawError")

    run(_go())


_ = EarnSource  # silence unused
