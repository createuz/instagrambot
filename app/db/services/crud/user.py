from typing import Any, Optional

from aiogram.types import User as AiogramUser
from aiogram_i18n.cores import BaseCore

from app.db.models import User
from app.db.models.dto import UserDto
from app.db.services.crud.base import CrudService
from app.db.services.postgres import SQLSessionContext
from app.db.services.redis import redis_cache
from app.const import DEFAULT_LOCALE, TIME_1M
from app.utils.key_builder import build_key


class UserService(CrudService):
    async def clear_cache(self, user_id: int) -> None:
        cache_key: str = build_key("cache", "get_user", user_id=user_id)
        await self.redis.delete(cache_key)

    async def create(
        self,
        aiogram_user: AiogramUser,
        i18n_core: BaseCore[Any],
        message_text: Optional[str] = None,
    ) -> UserDto:
        ref_by = (str(message_text).partition("=")[2]) or "bot"
        print(ref_by)
        db_user: User = User(
            chat_id=aiogram_user.id,
            username=aiogram_user.username,
            first_name=aiogram_user.first_name,
            language=(
                aiogram_user.language_code
                if aiogram_user.language_code in i18n_core.available_locales
                else DEFAULT_LOCALE
            ),
            language_code=aiogram_user.language_code,
            is_premium=getattr(aiogram_user, "is_premium", False),
            ref_by=ref_by,
        )

        async with SQLSessionContext(session_pool=self.session_pool) as (
            repository,
            uow,
        ):
            await uow.commit(db_user)

        await self.clear_cache(user_id=aiogram_user.id)
        return db_user.dto()

    @redis_cache(prefix="get_user", ttl=TIME_1M)
    async def get(self, user_id: int) -> Optional[UserDto]:
        async with SQLSessionContext(session_pool=self.session_pool) as (
            repository,
            uow,
        ):
            user = await repository.users.get(user_id=user_id)
            if user is None:
                return None
            return user.dto()

    async def count(self) -> int:
        async with SQLSessionContext(session_pool=self.session_pool) as (
            repository,
            uow,
        ):
            return await repository.users.count()

    async def update(self, user: UserDto, **data: Any) -> Optional[UserDto]:
        async with SQLSessionContext(session_pool=self.session_pool) as (
            repository,
            uow,
        ):
            for key, value in data.items():
                setattr(user, key, value)
            await self.clear_cache(user_id=user.chat_id)
            user_db = await repository.users.update(
                user_id=user.chat_id, **user.model_state
            )
            if user_db is None:
                return None
            return user_db.dto()
