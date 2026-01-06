from __future__ import annotations

from typing import Any, Awaitable, Callable, Optional

from aiogram.types import (
    CallbackQuery,
    ErrorEvent,
    Message,
    TelegramObject,
    Update,
)

from app.bot.helpers import MessageHelper
from app.bot.middlewares.event_typed import EventTypedMiddleware


class MessageHelperMiddleware(EventTypedMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: dict[str, Any],
    ) -> Any:
        update: Optional[TelegramObject] = event
        if isinstance(update, ErrorEvent):
            update = update.update
        if isinstance(update, Update):
            update = update.event
        if isinstance(update, (Message, CallbackQuery)):
            bot = data.get("bot")
            fsm_context = data.get("states")
            if bot is not None:
                data["helper"] = MessageHelper(
                    update=update,
                    bot=bot,
                    fsm_context=fsm_context,
                )
        return await handler(event, data)
