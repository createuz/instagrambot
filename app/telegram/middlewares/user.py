from __future__ import annotations

from typing import Any, Awaitable, Callable, Optional
from typing import TYPE_CHECKING

from aiogram.types import TelegramObject, CallbackQuery, Message, User as AiogramUser
from aiogram_i18n import I18nMiddleware
from sqlalchemy.exc import IntegrityError

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
        aiogram_user: Optional[AiogramUser] = data.get("event_from_user") or getattr(event, "from_user", None)
        if aiogram_user is None or getattr(aiogram_user, "is_bot", False):
            return await handler(event, data)
        message_text: Optional[str] = None
        if isinstance(event, Message):
            message_text = getattr(event, "text", None)
        elif isinstance(event, CallbackQuery) and event.message:
            message_text = getattr(event.message, "text", None)
        user_service: Optional[UserService] = data.get("user_service")
        if user_service is None:
            logger.warning("UserService is not provided in data; skipping user creation.")
            return await handler(event, data)
        try:
            user: Optional[UserDto] = await user_service.get(user_id=aiogram_user.id)
            if user is None:
                i18n: Optional[I18nMiddleware] = data.get("i18n_middleware")
                try:
                    user = await user_service.create(
                        aiogram_user=aiogram_user,
                        i18n_core=(i18n.core if i18n is not None else None),
                        message_text=message_text,
                    )
                    logger.info("New user in database: %s (%d)", aiogram_user.full_name, aiogram_user.id)
                except IntegrityError:
                    logger.info("Race creating user, fetching existing user for id=%s", aiogram_user.id)
                    user = await user_service.get(user_id=aiogram_user.id)

            data["user"] = user
            return await handler(event, data)

        except Exception as exc:
            logger.exception("User middleware failed for %s: %s", getattr(aiogram_user, "id", "?"), exc)
            return await handler(event, data)
