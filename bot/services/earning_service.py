"""Earnings, anti-spam cooldown, referral commission."""
from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from ..config import settings
from ..db import Earning, EarnSource, User


async def add_earning(
    session: AsyncSession,
    user: User,
    amount: int,
    source: EarnSource,
    note: str | None = None,
    pay_referral: bool = True,
) -> tuple[Earning, Earning | None]:
    """Add `amount` to user's balance, log it, and pay referral commission if enabled.

    Returns (earning_log, referral_earning_log_or_none).
    """
    if amount <= 0:
        raise ValueError("Earning amount must be positive")

    user.balance += amount
    user.total_earned += amount

    log = Earning(user_id=user.id, amount=amount, source=source.value, note=note)
    session.add(log)

    referral_log: Earning | None = None
    if (
        pay_referral
        and user.referrer_id is not None
        and source in (EarnSource.AD, EarnSource.TASK, EarnSource.DAILY)
    ):
        commission = amount * settings.referral_percent // 100
        if commission > 0:
            referrer = await session.get(User, user.referrer_id)
            if referrer is not None and not referrer.is_banned:
                referrer.balance += commission
                referrer.total_earned += commission
                referral_log = Earning(
                    user_id=referrer.id,
                    amount=commission,
                    source=EarnSource.REFERRAL.value,
                    note=f"komisi {settings.referral_percent}% dari user#{user.id}",
                )
                session.add(referral_log)

    await session.flush()
    return log, referral_log


def cooldown_remaining(user: User) -> int:
    """Return seconds remaining before user may watch another ad. 0 if ready."""
    if user.last_ad_at is None:
        return 0
    elapsed = (datetime.utcnow() - user.last_ad_at).total_seconds()
    remaining = settings.ad_cooldown_seconds - elapsed
    return max(0, int(remaining))


async def grant_ad_reward(session: AsyncSession, user: User) -> int:
    """Grant the configured per-ad reward, update counters, return amount granted."""
    user.last_ad_at = datetime.utcnow()
    user.ads_watched += 1
    await add_earning(
        session,
        user,
        settings.earn_per_ad,
        EarnSource.AD,
        note="rewarded ad view",
    )
    return settings.earn_per_ad


async def grant_referral_signup_bonus(
    session: AsyncSession, referrer: User, new_user: User
) -> int | None:
    """Pay signup bonus to referrer when a new user is created via their link."""
    bonus = settings.referral_signup_bonus
    if bonus <= 0:
        return None
    referrer.balance += bonus
    referrer.total_earned += bonus
    log = Earning(
        user_id=referrer.id,
        amount=bonus,
        source=EarnSource.REFERRAL_SIGNUP.value,
        note=f"signup bonus dari user#{new_user.id}",
    )
    session.add(log)
    await session.flush()
    return bonus


def can_claim_daily(user: User) -> bool:
    if user.last_daily_at is None:
        return True
    return (datetime.utcnow() - user.last_daily_at) >= timedelta(hours=20)
