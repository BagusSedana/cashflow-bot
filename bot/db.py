"""SQLAlchemy async setup + ORM models."""
from __future__ import annotations

from datetime import datetime
from enum import Enum

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from .config import settings


class Base(DeclarativeBase):
    pass


def _utcnow() -> datetime:
    return datetime.utcnow()


class WithdrawStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    PAID = "paid"


class EarnSource(str, Enum):
    AD = "ad"
    TASK = "task"
    REFERRAL = "referral"
    REFERRAL_SIGNUP = "referral_signup"
    BONUS = "bonus"
    DAILY = "daily"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(
        BigInteger, unique=True, index=True, nullable=False
    )
    username: Mapped[str | None] = mapped_column(String(64), nullable=True)
    first_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    language_code: Mapped[str | None] = mapped_column(String(8), nullable=True)

    # Saldo dalam rupiah utuh (integer). 1 satuan = 1 rupiah.
    balance: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_earned: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_withdrawn: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    ads_watched: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_ad_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_daily_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    referrer_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )
    is_banned: Mapped[bool] = mapped_column(default=False, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    referrer: Mapped["User | None"] = relationship(
        "User", remote_side="User.id", foreign_keys=[referrer_id]
    )


class Earning(Base):
    __tablename__ = "earnings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), index=True, nullable=False
    )
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    source: Mapped[str] = mapped_column(String(32), nullable=False)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )


class WithdrawRequest(Base):
    __tablename__ = "withdraw_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), index=True, nullable=False
    )
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    method: Mapped[str] = mapped_column(String(32), nullable=False)
    account_number: Mapped[str] = mapped_column(String(64), nullable=False)
    account_name: Mapped[str] = mapped_column(String(128), nullable=False)

    status: Mapped[str] = mapped_column(
        String(16), default=WithdrawStatus.PENDING.value, nullable=False
    )
    admin_note: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    processed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


engine = create_async_engine(settings.database_url, echo=False, future=True)
SessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)


async def init_db() -> None:
    """Create tables if they don't exist. Quick & dirty for MVP — switch to Alembic later."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
