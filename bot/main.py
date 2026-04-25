"""Bot entrypoint: build dispatcher, register handlers, start polling."""
from __future__ import annotations

import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from .config import settings
from .db import init_db
from .handlers import admin, earn, menu, start, withdraw
from .middlewares.banned import BannedUserMiddleware


def configure_logging() -> None:
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )


async def main() -> None:
    configure_logging()
    log = logging.getLogger("cashflow-bot")

    # Make sure SQLite directory exists when using default file path
    if settings.database_url.startswith("sqlite"):
        path = settings.database_url.split("///", 1)[-1]
        directory = os.path.dirname(path) or "."
        os.makedirs(directory, exist_ok=True)

    await init_db()
    log.info("Database ready")

    bot = Bot(
        token=settings.telegram_bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=MemoryStorage())

    dp.message.middleware(BannedUserMiddleware())
    dp.callback_query.middleware(BannedUserMiddleware())

    dp.include_router(start.router)
    dp.include_router(admin.router)
    dp.include_router(withdraw.router)
    dp.include_router(earn.router)
    dp.include_router(menu.router)

    me = await bot.get_me()
    log.info("Bot started: @%s (id=%s) brand=%s", me.username, me.id, settings.brand_name)

    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()


def run() -> None:
    asyncio.run(main())


if __name__ == "__main__":
    run()
