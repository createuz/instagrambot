# app/utils/user_service.py
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repo_user import (
    get_language as repo_get_language,
    ensure_user as repo_ensure_user,
    upsert_language as repo_upsert_language,
)
from app.utils.redis_manager import RedisManager
from app.core.logger import get_logger

logger = get_logger()
CACHE_TTL = 7 * 24 * 3600  # 7 kun

async def redis_get_lang(redis_client, chat_id: int) -> Optional[str]:
    if not redis_client:
        return None
    try:
        key = f"user:{chat_id}:lang"
        val = await redis_client.get(key)
        if val is None:
            return None
        if isinstance(val, bytes):
            try:
                return val.decode()
            except Exception:
                return val.decode("utf-8", errors="ignore")
        return str(val)
    except Exception as e:
        logger.warning("redis_get_lang error for %s: %s", chat_id, e)
        return None

async def get_lang_cache_then_db(session: AsyncSession, chat_id: int) -> Optional[str]:
    redis = RedisManager.client()
    # 1) redis
    lang = await redis_get_lang(redis, chat_id)
    if lang:
        logger.info("redis hit %s -> %s", chat_id, lang)
        return lang

    # 2) db
    try:
        lang = await repo_get_language(session, chat_id)
        if lang:
            logger.info("DB hit %s -> %s", chat_id, lang)
            try:
                if redis:
                    await redis.set(f"user:{chat_id}:lang", lang, ex=CACHE_TTL)
                    logger.info("redis set %s -> %s", chat_id, lang)
            except Exception as e:
                logger.warning("redis set failed for %s: %s", chat_id, e)
        return lang
    except Exception as e:
        logger.exception("db_get_lang error for %s: %s", chat_id, e)
        return None

async def ensure_user_exists(session: AsyncSession, chat_id: int, username: Optional[str], first_name: Optional[str],
                             is_premium: Optional[bool], added_by: Optional[str] = None) -> int:
    """
    Ensure user row exists (language stays NULL). Returns user_id.
    Caller (handler/middleware) is responsible for commit (middleware will if session.info["writes"] set).
    """
    return await repo_ensure_user(session=session, chat_id=chat_id, username=username, first_name=first_name, is_premium=is_premium, added_by=added_by)

async def set_language_and_cache(session: AsyncSession, chat_id: int, language: str) -> int:
    """
    Update DB (or insert) and update Redis (best-effort).
    """
    user_id = await repo_upsert_language(session=session, chat_id=chat_id, language=language)
    # try cache
    try:
        redis = RedisManager.client()
        if redis:
            await redis.set(f"user:{chat_id}:lang", language, ex=CACHE_TTL)
    except Exception:
        logger.warning("set_language_and_cache: redis set failed for %s", chat_id)
    return user_id
