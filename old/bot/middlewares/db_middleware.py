# old/bot/middlewares/db_middleware.py
from typing import Callable, Any, Awaitable

from aiogram import BaseMiddleware

from old.core.logger import get_logger
from old.db.sessions.lazy_session import LazySessionProxy
from old.db.sessions.session import AsyncSessionLocal


class DBSessionMiddleware(BaseMiddleware):
    async def __call__(self, handler: Callable[[Any, dict], Awaitable[Any]], event: Any, data: dict):
        logger = get_logger()
        proxy = LazySessionProxy(session_maker=AsyncSessionLocal)
        data["db"] = proxy

        try:
            result = await handler(event, data)

            # If session was never created (no DB access) — do nothing.
            if not proxy.session_created:
                logger.debug("DBSessionMiddleware: no session created")
                return result

            session = proxy.get_underlying_session()
            if not session:
                logger.debug("DBSessionMiddleware: session missing -> nothing to do")
                return result

            # If handler committed explicitly -> skip commit
            if session.info.get("committed_by_handler"):
                logger.debug("DBSessionMiddleware: skipping commit, handler already committed")
                await session.close()
                return result

            # Commit only if actual writes happened (or SQLAlchemy tracked new/dirty/deleted)
            writes_flag = bool(session.info.get("writes", False))
            has_changes = bool(session.new) or bool(session.dirty) or bool(session.deleted) or writes_flag

            if has_changes:
                await session.commit()
                logger.info("DBSessionMiddleware: committed",
                            reason="writes_flag" if writes_flag else "session_new_dirty_deleted",
                            writes=writes_flag, new=len(session.new), dirty=len(session.dirty),
                            deleted=len(session.deleted))
            else:
                logger.debug("DBSessionMiddleware: nothing to commit (read-only)")

            await session.close()
            return result

        except Exception as exc:
            # rollback only if session was created and handler didn't commit
            if proxy.session_created:
                session = proxy.get_underlying_session()
                if session and not session.info.get("committed_by_handler"):
                    try:
                        await session.rollback()
                        logger.info("DBSessionMiddleware: rolled back due to exception")
                    except Exception:
                        logger.exception("DBSessionMiddleware: rollback failed")
                try:
                    if session:
                        await session.close()
                except Exception:
                    logger.exception("DBSessionMiddleware: session close failed")
            logger.exception("Exception in handler")
            raise
