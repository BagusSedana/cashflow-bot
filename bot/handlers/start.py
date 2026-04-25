"""/start handler — registers user, handles referrals."""
from __future__ import annotations

from aiogram import Bot, Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.utils.deep_linking import decode_payload

from .. import keyboards, texts
from ..db import SessionLocal
from ..services.earning_service import grant_referral_signup_bonus
from ..services.user_service import get_or_create_user, get_user_by_id

router = Router(name="start")


def _parse_referrer(payload: str | None) -> int | None:
    if not payload:
        return None
    try:
        decoded = decode_payload(payload)
    except Exception:
        decoded = payload
    if decoded.startswith("ref_"):
        candidate = decoded[4:]
    else:
        candidate = decoded
    try:
        return int(candidate)
    except ValueError:
        return None


@router.message(CommandStart(deep_link=True))
@router.message(CommandStart())
async def cmd_start(message: Message, bot: Bot, command=None) -> None:  # noqa: ANN001
    if message.from_user is None:
        return

    payload: str | None = None
    if command is not None and getattr(command, "args", None):
        payload = command.args

    referrer_telegram_id = _parse_referrer(payload)

    async with SessionLocal() as session:
        user, created = await get_or_create_user(
            session, message.from_user, referrer_telegram_id
        )

        if user.is_banned:
            await session.commit()
            await message.answer(texts.BANNED_NOTICE)
            return

        bonus_amount: int | None = None
        referrer_telegram_id_for_notify: int | None = None
        if created and user.referrer_id is not None:
            referrer = await get_user_by_id(session, user.referrer_id)
            if referrer is not None and not referrer.is_banned:
                bonus_amount = await grant_referral_signup_bonus(
                    session, referrer, user
                )
                referrer_telegram_id_for_notify = referrer.telegram_id

        await session.commit()

    await message.answer(
        texts.welcome(message.from_user.first_name),
        reply_markup=keyboards.main_menu(),
    )

    if bonus_amount and referrer_telegram_id_for_notify:
        try:
            await bot.send_message(
                referrer_telegram_id_for_notify,
                texts.REFERRAL_SIGNUP_NOTIFY.format(
                    name=message.from_user.first_name or "Sobat",
                    bonus=texts.fmt_rp(bonus_amount),
                ),
            )
        except Exception:
            pass
