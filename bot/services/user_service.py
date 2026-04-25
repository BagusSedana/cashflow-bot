"""User-related DB helpers."""
from __future__ import annotations

from aiogram.types import User as TgUser
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import Earning, EarnSource, User


async def get_or_create_user(
    session: AsyncSession,
    tg_user: TgUser,
    referrer_telegram_id: int | None = None,
) -> tuple[User, bool]:
    """Return (user, created)."""
    result = await session.execute(
        select(User).where(User.telegram_id == tg_user.id)
    )
    user = result.scalar_one_or_none()
    if user is not None:
        return user, False

    referrer = None
    if referrer_telegram_id and referrer_telegram_id != tg_user.id:
        ref_result = await session.execute(
            select(User).where(User.telegram_id == referrer_telegram_id)
        )
        referrer = ref_result.scalar_one_or_none()

    user = User(
        telegram_id=tg_user.id,
        username=tg_user.username,
        first_name=tg_user.first_name,
        language_code=tg_user.language_code,
        referrer_id=referrer.id if referrer else None,
    )
    session.add(user)
    await session.flush()
    return user, True


async def get_user_by_telegram_id(
    session: AsyncSession, telegram_id: int
) -> User | None:
    result = await session.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    return result.scalar_one_or_none()


async def get_user_by_id(session: AsyncSession, user_id: int) -> User | None:
    return await session.get(User, user_id)


async def referral_stats(session: AsyncSession, user: User) -> tuple[int, int]:
    """Return (count_of_direct_referrals, total_referral_earnings_received)."""
    count_result = await session.execute(
        select(func.count(User.id)).where(User.referrer_id == user.id)
    )
    count = int(count_result.scalar() or 0)

    earn_result = await session.execute(
        select(func.coalesce(func.sum(Earning.amount), 0)).where(
            Earning.user_id == user.id,
            Earning.source.in_(
                [EarnSource.REFERRAL.value, EarnSource.REFERRAL_SIGNUP.value]
            ),
        )
    )
    total = int(earn_result.scalar() or 0)
    return count, total
