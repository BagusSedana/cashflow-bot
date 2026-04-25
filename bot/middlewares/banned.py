"""Middleware: short-circuit any update from banned users."""
from __future__ import annotations

from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject, User

from .. import texts
from ..db import SessionLocal
from ..services.user_service import get_user_by_telegram_id


class BannedUserMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        tg_user: User | None = data.get("event_from_user")
        if tg_user is None:
            return await handler(event, data)

        async with SessionLocal() as session:
            db_user = await get_user_by_telegram_id(session, tg_user.id)
            if db_user is not None and db_user.is_banned:
                if isinstance(event, Message):
                    await event.answer(texts.BANNED_NOTICE)
                elif isinstance(event, CallbackQuery):
                    await event.answer(texts.BANNED_NOTICE, show_alert=True)
                return None

        return await handler(event, data)
