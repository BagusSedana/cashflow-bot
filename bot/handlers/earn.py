"""Watch ad / earning entrypoint.

For MVP this is a "mock ad" — user clicks button, gets reward after cooldown.
Once a Telegram Mini App is wired up with Adsgram/Monetag SDK, replace
`grant_ad_reward` with a callback that's only granted after the SDK fires
its onReward event server-side (so it can't be spoofed).
"""
from __future__ import annotations

import asyncio

from aiogram import Bot, F, Router
from aiogram.types import CallbackQuery, Message

from .. import keyboards, texts
from ..db import SessionLocal, EarnSource
from ..services.earning_service import (
    cooldown_remaining,
    grant_ad_reward,
)
from ..services.user_service import get_user_by_id, get_user_by_telegram_id

router = Router(name="earn")


@router.message(F.text == texts.MENU_BUTTON_EARN)
async def on_watch_button(message: Message) -> None:
    from ..config import settings as _s

    if _s.ad_cooldown_seconds > 0:
        cooldown_line = f"Cooldown antar iklan: {_s.ad_cooldown_seconds} detik\n\n"
    else:
        cooldown_line = "Tonton sebanyak yang kamu mau, langsung lanjut.\n\n"
    await message.answer(
        "🎬 <b>Tonton Iklan</b>\n\n"
        f"Setiap iklan = <b>{texts.fmt_rp(_s.earn_per_ad)}</b>\n"
        f"{cooldown_line}"
        "Klik tombol di bawah untuk mulai:",
        reply_markup=keyboards.watch_button(),
    )


@router.callback_query(F.data == "watch_ad")
async def on_watch_ad(query: CallbackQuery, bot: Bot) -> None:
    if query.from_user is None:
        await query.answer()
        return

    async with SessionLocal() as session:
        user = await get_user_by_telegram_id(session, query.from_user.id)
        if user is None:
            await query.answer("Ketik /start dulu untuk daftar.", show_alert=True)
            return
        if user.is_banned:
            await query.answer("Akun kamu dinonaktifkan.", show_alert=True)
            return

        remaining = cooldown_remaining(user)
        if remaining > 0:
            await query.answer(
                texts.AD_COOLDOWN_NOT_READY.format(seconds=remaining),
                show_alert=True,
            )
            return

        # Mock "watching": acknowledge and wait, then grant.
        # In production, replace with Mini App callback that the Adsgram SDK
        # fires on actual ad completion.
        await query.answer("⏳ Memutar iklan...")
        await asyncio.sleep(2)

        amount = await grant_ad_reward(session, user)
        balance = user.balance
        referrer_id = user.referrer_id
        await session.commit()

    if query.message is not None and isinstance(query.message, Message):
        await query.message.answer(
            texts.AD_REWARD_GRANTED.format(
                amount=texts.fmt_rp(amount),
                balance=texts.fmt_rp(balance),
            ),
            reply_markup=keyboards.watch_again(),
        )

    # Notify upline (best-effort)
    if referrer_id is not None:
        try:
            async with SessionLocal() as session:
                referrer = await get_user_by_id(session, referrer_id)
            if referrer is not None and not referrer.is_banned:
                from ..config import settings as _s

                commission = amount * _s.referral_percent // 100
                if commission > 0:
                    await bot.send_message(
                        referrer.telegram_id,
                        texts.REFERRAL_EARNING_NOTIFY.format(
                            name=query.from_user.first_name or "Sobat",
                            amount=texts.fmt_rp(commission),
                        ),
                    )
        except Exception:
            pass


# Suppress unused import warning — EarnSource may be used by future task handlers
_ = EarnSource
