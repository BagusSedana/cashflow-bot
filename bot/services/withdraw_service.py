"""Withdraw request lifecycle."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import settings
from ..db import User, WithdrawRequest, WithdrawStatus


class WithdrawError(Exception):
    pass


async def create_request(
    session: AsyncSession,
    user: User,
    amount: int,
    method: str,
    account_number: str,
    account_name: str,
) -> WithdrawRequest:
    if amount < settings.min_withdraw:
        raise WithdrawError(f"Minimum {settings.min_withdraw}")
    if amount > settings.max_withdraw:
        raise WithdrawError(f"Maksimum per request {settings.max_withdraw}")
    if amount > user.balance:
        raise WithdrawError("Saldo tidak cukup")
    if method not in settings.payout_methods:
        raise WithdrawError("Metode pembayaran tidak valid")

    user.balance -= amount

    req = WithdrawRequest(
        user_id=user.id,
        amount=amount,
        method=method,
        account_number=account_number,
        account_name=account_name,
        status=WithdrawStatus.PENDING.value,
    )
    session.add(req)
    await session.flush()
    return req


async def get_request(
    session: AsyncSession, request_id: int
) -> WithdrawRequest | None:
    return await session.get(WithdrawRequest, request_id)


async def approve(
    session: AsyncSession, req: WithdrawRequest, admin_note: str | None = None
) -> None:
    if req.status != WithdrawStatus.PENDING.value:
        raise WithdrawError("Request bukan PENDING")
    req.status = WithdrawStatus.APPROVED.value
    req.processed_at = datetime.utcnow()
    if admin_note:
        req.admin_note = admin_note


async def reject(
    session: AsyncSession,
    req: WithdrawRequest,
    reason: str,
) -> None:
    if req.status not in (WithdrawStatus.PENDING.value, WithdrawStatus.APPROVED.value):
        raise WithdrawError("Request sudah final, tidak bisa di-reject")

    user = await session.get(User, req.user_id)
    if user is not None:
        user.balance += req.amount

    req.status = WithdrawStatus.REJECTED.value
    req.processed_at = datetime.utcnow()
    req.admin_note = reason


async def mark_paid(
    session: AsyncSession,
    req: WithdrawRequest,
    admin_note: str | None = None,
) -> None:
    if req.status not in (
        WithdrawStatus.APPROVED.value,
        WithdrawStatus.PENDING.value,
    ):
        raise WithdrawError("Request bukan APPROVED/PENDING")
    req.status = WithdrawStatus.PAID.value
    req.processed_at = datetime.utcnow()
    if admin_note:
        req.admin_note = admin_note

    user = await session.get(User, req.user_id)
    if user is not None:
        user.total_withdrawn += req.amount


async def list_pending(session: AsyncSession, limit: int = 20) -> list[WithdrawRequest]:
    result = await session.execute(
        select(WithdrawRequest)
        .where(WithdrawRequest.status == WithdrawStatus.PENDING.value)
        .order_by(WithdrawRequest.created_at.asc())
        .limit(limit)
    )
    return list(result.scalars().all())


async def seconds_since_last_request(
    session: AsyncSession, user_id: int
) -> int | None:
    """Return seconds since the user's most recent non-rejected withdraw request.

    Returns None when the user has no prior withdraw request.
    """
    result = await session.execute(
        select(WithdrawRequest.created_at)
        .where(WithdrawRequest.user_id == user_id)
        .where(WithdrawRequest.status != WithdrawStatus.REJECTED.value)
        .order_by(WithdrawRequest.created_at.desc())
        .limit(1)
    )
    last = result.scalar_one_or_none()
    if last is None:
        return None
    return int((datetime.utcnow() - last).total_seconds())
