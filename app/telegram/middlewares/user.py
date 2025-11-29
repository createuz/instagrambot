from __future__ import annotations

from typing import TYPE_CHECKING, Any, Awaitable, Callable, Optional

from aiogram.types import TelegramObject, CallbackQuery, Message, User as AiogramUser
from aiogram_i18n import I18nMiddleware

from app.db.services.crud.user import UserService
from app.telegram.middlewares.event_typed import EventTypedMiddleware
from app.utils.logging import database as logger

if TYPE_CHECKING:
    from app.db.models.dto import UserDto


class UserMiddleware(EventTypedMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: dict[str, Any],
    ) -> Optional[Any]:
        aiogram_user: Optional[AiogramUser] = data.get("event_from_user")
        if aiogram_user is None or getattr(aiogram_user, "is_bot", False):
            return await handler(event, data)
        message_text: Optional[str] = None
        if isinstance(event, Message):
            message_text = getattr(event, "text", None)
        elif isinstance(event, CallbackQuery) and event.message:
            message_text = getattr(event.message, "text", None)
        user_service: UserService = data["user_service"]
        try:
            user: Optional[UserDto] = await user_service.get(user_id=aiogram_user.id)
            if user is None:
                i18n: I18nMiddleware = data.get("i18n_middleware")
                user = await user_service.create(
                    aiogram_user=aiogram_user,
                    i18n_core=i18n.core,
                    message_text=message_text,
                )
                logger.info("New user in database: %s (%d)", aiogram_user.full_name, aiogram_user.id)
            data["user"] = user
            return await handler(event, data)
        except Exception as exc:
            logger.exception("User middleware failed for %s: %s", getattr(aiogram_user, "id", "?"), exc)
            return None
