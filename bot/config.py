"""App configuration loaded from environment variables.

Note: list-style env vars (`ADMIN_IDS`, `PAYOUT_METHODS`) are stored as raw
comma-separated strings on this Settings model and exposed as parsed lists via
`@property`. This avoids pydantic-settings' default JSON-decoding behavior on
list-typed fields, which would reject simple values like ``DANA,GoPay,OVO``.
"""
from __future__ import annotations

from pydantic import Field
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
    admin_ids_raw: str = Field(default="", alias="ADMIN_IDS")
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
    payout_methods_raw: str = Field(
        default="DANA,GoPay,OVO,BANK", alias="PAYOUT_METHODS"
    )
    withdraw_cooldown_seconds: int = Field(
        default=3600, alias="WITHDRAW_COOLDOWN_SECONDS"
    )

    # Daily check-in
    daily_bonus_min: int = Field(default=100, alias="DAILY_BONUS_MIN")
    daily_bonus_max: int = Field(default=300, alias="DAILY_BONUS_MAX")

    # Mini App / Adsgram (v0.2 — real ads)
    webapp_url: str = Field(default="", alias="WEBAPP_URL")
    webapp_host: str = Field(default="0.0.0.0", alias="WEBAPP_HOST")
    webapp_port: int = Field(default=8080, alias="WEBAPP_PORT")
    adsgram_block_id: str = Field(default="", alias="ADSGRAM_BLOCK_ID")

    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    @property
    def admin_ids(self) -> list[int]:
        return [int(v.strip()) for v in self.admin_ids_raw.split(",") if v.strip()]

    @property
    def payout_methods(self) -> list[str]:
        items = [v.strip() for v in self.payout_methods_raw.split(",") if v.strip()]
        return items or ["DANA", "GoPay", "OVO", "BANK"]


settings = Settings()  # type: ignore[call-arg]
