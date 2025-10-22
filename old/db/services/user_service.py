# old/utils/user_service.py
from typing import Optional

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from old.core.logger import get_logger
from old.db.services.user_repo import UserRepo

logger = get_logger()
repo = UserRepo(logger=logger)

CACHE_TTL = 7 * 24 * 3600  # one week


def _lang_key(chat_id: int) -> str:
    return f"user:{chat_id}:lang"


async def redis_get_lang(redis_client, chat_id: int) -> Optional[str]:
    if redis_client is None:
        return None
    try:
        val = await redis_client.get(_lang_key(chat_id))
        if val is None:
            return None
        if isinstance(val, bytes):
            return val.decode("utf-8", errors="ignore")
        return str(val)
    except Exception as e:
        logger.warning("redis_get_lang error for %s: %s", chat_id, e)
        return None


async def redis_set_lang(redis_client, chat_id: int, lang: str) -> None:
    if redis_client is None:
        return
    try:
        await redis_client.set(_lang_key(chat_id), lang, ex=CACHE_TTL)
    except Exception as e:
        logger.warning("redis_set_lang failed for %s: %s", chat_id, e)


async def get_lang_cache_then_db(session: AsyncSession, redis_client, chat_id: int) -> Optional[str]:
    lang = await redis_get_lang(redis_client, chat_id)
    if lang:
        logger.debug("get_lang_cache_then_db: redis hit %s -> %s", chat_id, lang)
        return lang
    try:
        lang = await repo.get_language(session, chat_id)
        if lang:
            logger.debug("get_lang_cache_then_db: db hit %s -> %s", chat_id, lang)
            await redis_set_lang(redis_client, chat_id, lang)
        return lang
    except SQLAlchemyError as e:
        logger.exception("get_lang_cache_then_db DB failed for %s: %s", chat_id, e)
        return None


async def ensure_user_exists(
        session: AsyncSession,
        chat_id: int,
        username: Optional[str],
        first_name: Optional[str],
        is_premium: Optional[bool],
        default_lang: Optional[str] = None,
        added_by: Optional[str] = None
) -> int:
    return await repo.ensure_user(
        session=session,
        chat_id=chat_id,
        username=username,
        first_name=first_name,
        is_premium=is_premium,
        default_lang=default_lang,
        added_by=added_by,
    )


async def upsert_user_language(session: AsyncSession, redis_client, chat_id: int, language: str) -> int:
    user_id = await repo.upsert_language(session=session, chat_id=chat_id, language=language)
    await redis_set_lang(redis_client, chat_id, language)
    return user_id


async def set_language_and_cache(session: AsyncSession, redis_client, chat_id: int, language: str) -> int:
    return await upsert_user_language(session, redis_client, chat_id, language)
