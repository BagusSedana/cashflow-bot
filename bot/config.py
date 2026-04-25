"""App configuration loaded from environment variables."""
from __future__ import annotations

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Telegram
    telegram_bot_token: str = Field(..., alias="TELEGRAM_BOT_TOKEN")
    admin_ids: list[int] = Field(default_factory=list, alias="ADMIN_IDS")
    proof_channel_username: str = Field(default="", alias="PROOF_CHANNEL_USERNAME")

    # App
    database_url: str = Field(
        default="sqlite+aiosqlite:///./data/bot.db", alias="DATABASE_URL"
    )
    brand_name: str = Field(default="CashFlow ID", alias="BRAND_NAME")

    # Earning rates
    earn_per_ad: int = Field(default=10, alias="EARN_PER_AD")
    ad_cooldown_seconds: int = Field(default=30, alias="AD_COOLDOWN_SECONDS")
    referral_percent: int = Field(default=5, alias="REFERRAL_PERCENT")
    referral_signup_bonus: int = Field(default=500, alias="REFERRAL_SIGNUP_BONUS")

    # Withdraw
    min_withdraw: int = Field(default=5_000, alias="MIN_WITHDRAW")
    max_withdraw: int = Field(default=500_000, alias="MAX_WITHDRAW")
    payout_methods: list[str] = Field(
        default_factory=lambda: ["DANA", "GoPay", "OVO", "BANK"],
        alias="PAYOUT_METHODS",
    )

    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    @field_validator("admin_ids", mode="before")
    @classmethod
    def _parse_admin_ids(cls, value: object) -> list[int]:
        if value in (None, "", []):
            return []
        if isinstance(value, int):
            return [value]
        if isinstance(value, list):
            return [int(v) for v in value if str(v).strip()]
        if isinstance(value, str):
            return [int(v.strip()) for v in value.split(",") if v.strip()]
        raise TypeError(f"Unsupported admin_ids value: {value!r}")

    @field_validator("payout_methods", mode="before")
    @classmethod
    def _parse_payout_methods(cls, value: object) -> list[str]:
        if value in (None, "", []):
            return ["DANA", "GoPay", "OVO", "BANK"]
        if isinstance(value, list):
            return [str(v).strip() for v in value if str(v).strip()]
        if isinstance(value, str):
            return [v.strip() for v in value.split(",") if v.strip()]
        raise TypeError(f"Unsupported payout_methods value: {value!r}")


settings = Settings()  # type: ignore[call-arg]
