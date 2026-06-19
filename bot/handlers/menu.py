"""Main menu handlers: balance, referral, help, proof, daily check-in."""
from __future__ import annotations

import random
from datetime import datetime

from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from .. import keyboards, texts
from ..config import settings
from ..db import EarnSource, SessionLocal
from ..services.earning_service import add_earning, can_claim_daily
from ..services.user_service import get_user_by_telegram_id, referral_stats

router = Router(name="menu")


async def _show_balance(message: Message) -> None:
    if message.from_user is None:
        return
    async with SessionLocal() as session:
        user = await get_user_by_telegram_id(session, message.from_user.id)
        if user is None:
            await message.answer("Silakan ketik /start dulu untuk mendaftar.")
            return
        await message.answer(texts.balance_view(user))


@router.message(F.text == texts.MENU_BUTTON_BALANCE)
async def on_balance(message: Message) -> None:
    await _show_balance(message)


@router.callback_query(F.data == "show_balance")
async def on_balance_cb(query: CallbackQuery) -> None:
    if query.message is None or not isinstance(query.message, Message):
        await query.answer()
        return
    if query.from_user is None:
        await query.answer()
        return
    async with SessionLocal() as session:
        user = await get_user_by_telegram_id(session, query.from_user.id)
        if user is None:
            await query.answer("Ketik /start dulu.", show_alert=True)
            return
        await query.message.answer(texts.balance_view(user))
    await query.answer()


@router.message(F.text == texts.MENU_BUTTON_REFERRAL)
async def on_referral(message: Message, bot: Bot) -> None:
    if message.from_user is None:
        return
    me = await bot.get_me()
    bot_username = me.username or "your_bot"

    async with SessionLocal() as session:
        user = await get_user_by_telegram_id(session, message.from_user.id)
        if user is None:
            await message.answer("Silakan ketik /start dulu.")
            return
        ref_count, ref_earnings = await referral_stats(session, user)

    await message.answer(
        texts.referral_view(user, bot_username, ref_count, ref_earnings)
    )


@router.message(F.text == texts.MENU_BUTTON_HELP)
async def on_help(message: Message) -> None:
    await message.answer(texts.help_text())


@router.message(F.text == texts.MENU_BUTTON_PROOF)
async def on_proof(message: Message) -> None:
    if not settings.proof_channel_username:
        await message.answer("Channel bukti pembayaran belum dikonfigurasi.")
        return
    await message.answer(
        f"📢 Channel bukti pembayaran:\n"
        f"https://t.me/{settings.proof_channel_username}"
    )


@router.message(F.text == texts.MENU_BUTTON_TASKS)
async def on_tasks(message: Message) -> None:
    await message.answer(
        "📋 <b>Tugas Berbayar</b>\n\n"
        "Fitur ini sedang dalam pengembangan dan akan segera tersedia.\n"
        "Sementara, kamu bisa earn lewat menu Tonton Iklan atau ajak teman.",
        reply_markup=keyboards.main_menu(),
    )


@router.message(Command("daily"))
@router.message(F.text == texts.MENU_BUTTON_DAILY)
async def on_daily(message: Message) -> None:
    if message.from_user is None:
        return
    async with SessionLocal() as session:
        user = await get_user_by_telegram_id(session, message.from_user.id)
        if user is None:
            await message.answer("Ketik /start dulu.")
            return
        if not can_claim_daily(user):
            await message.answer(
                "🎁 <b>Bonus Harian</b>\n\n"
                "Kamu sudah klaim hari ini. Datang lagi besok ya 👋"
            )
            return

        lo = max(0, settings.daily_bonus_min)
        hi = max(lo, settings.daily_bonus_max)
        amount = random.randint(lo, hi) if hi >= lo else 0
        if amount <= 0:
            await message.answer(
                "Bonus harian sedang dinonaktifkan oleh admin (DAILY_BONUS_MAX=0)."
            )
            return

        user.last_daily_at = datetime.utcnow()
        await add_earning(
            session,
            user,
            amount,
            EarnSource.DAILY,
            note="daily check-in",
            pay_referral=False,
        )
        balance = user.balance
        await session.commit()

    await message.answer(
        f"🎁 <b>Bonus Harian</b>\n\n"
        f"Kamu dapat <b>{texts.fmt_rp(amount)}</b>! 🎉\n"
        f"Saldo sekarang: <b>{texts.fmt_rp(balance)}</b>\n\n"
        f"Datang lagi besok ya, bonus reset tiap 20 jam."
    )
