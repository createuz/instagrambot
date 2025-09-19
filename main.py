# # main.py
# import asyncio
# import signal
#
# from redis.asyncio import Redis
#
# from app.bot.handlers.admins import panel, statistics, ads, server
# from app.bot.handlers.users import start
# from app.bot.middlewares.db_middleware import DBSessionMiddleware
# from app.bot.middlewares.update_middleware import ChatLoggerMiddleware
# from app.bot.utils import get_dispatcher, get_redis_storage
# from app.core import conf
# from app.core.config import bot
# from app.core.logger import get_logger
# from app.db.services.redis_manager import RedisManager
# from app.db.sessions.session import init_db, dispose_db
#
# logger = get_logger()
#
#
# async def create_bot_and_dp():
#     storage = get_redis_storage(redis=Redis.from_url(conf.redis.url_or_build()))
#     dp = get_dispatcher(storage=storage)
#     dp.update.outer_middleware(DBSessionMiddleware())
#     dp.update.outer_middleware(ChatLoggerMiddleware(logger=logger))
#     dp.include_router(start.router)
#     dp.include_router(panel.router)
#     dp.include_router(statistics.router)
#     dp.include_router(ads.router)
#     dp.include_router(server.router)
#     return bot, dp
#
#
# async def startup(bot, dp):
#     await RedisManager.init()
#     await init_db()
#     logger.info("startup finished")
#
#
# async def shutdown(bot, dp):
#     try:
#         await dp.storage.close()
#     except Exception:
#         logger.exception("closing storage failed")
#     try:
#         await bot.session.close()
#     except Exception:
#         logger.exception("closing bot session failed")
#     await RedisManager.close()
#     await dispose_db()
#     logger.info("shutdown finished")
#
#
# async def run_polling():
#     bot, dp = await create_bot_and_dp()
#     await startup(bot, dp)
#
#     loop = asyncio.get_running_loop()
#     stop_event = asyncio.Event()
#
#     def _on_sig():
#         logger.info("signal received")
#         stop_event.set()
#
#     for s in (signal.SIGINT, signal.SIGTERM):
#         try:
#             loop.add_signal_handler(s, _on_sig)
#         except NotImplementedError:
#             pass
#     await bot.delete_webhook(drop_pending_updates=True)
#     polling_task = asyncio.create_task(dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types()))
#     stop_task = asyncio.create_task(stop_event.wait())
#     done, pending = await asyncio.wait([polling_task, stop_task], return_when=asyncio.FIRST_COMPLETED)
#
#     if not polling_task.done():
#         try:
#             await dp.stop_polling()
#         except Exception:
#             logger.exception("stop polling failed")
#
#     for t in (polling_task, stop_task):
#         if not t.done():
#             t.cancel()
#             try:
#                 await t
#             except asyncio.CancelledError:
#                 pass
#
#     await shutdown(bot, dp)
#
#
# if __name__ == "__main__":
#     try:
#         asyncio.run(run_polling())
#     except KeyboardInterrupt:
#         pass

# main.py
import asyncio
import signal
from typing import Tuple, Optional

from aiogram import Bot, Dispatcher
from redis.asyncio import Redis

from app.bot.handlers.admins import panel, statistics, ads, server
from app.bot.handlers.users import start
from app.bot.middlewares.db_middleware import DBSessionMiddleware
from app.bot.middlewares.update_middleware import ChatLoggerMiddleware
from app.bot.utils import get_dispatcher, get_redis_storage
from app.core import conf
from app.core.config import bot
from app.core.logger import get_logger
from app.db.services.redis_manager import RedisManager
from app.db.sessions.session import init_db, dispose_db

logger = get_logger()

# Tunable timeouts
STOP_TIMEOUT = 20.0  # time to wait for dispatcher to stop polling gracefully
CLOSE_TIMEOUT = 10.0  # time to wait for each resource close


async def _close_with_timeout(coro, name: str, timeout: float = CLOSE_TIMEOUT):
    try:
        return await asyncio.wait_for(coro, timeout=timeout)
    except asyncio.TimeoutError:
        logger.warning("%s did not finish within %.1fs", name, timeout)
    except Exception:
        logger.exception("Error while closing %s", name)


async def create_bot_and_dp() -> Tuple[Bot, Dispatcher]:
    """Create and configure bot and dispatcher (middlewares + routers)."""
    storage = get_redis_storage(redis=Redis.from_url(conf.redis.url_or_build()))
    dp: Dispatcher = get_dispatcher(storage=storage)

    # Middlewares (outer: applied to all updates)
    dp.update.outer_middleware(DBSessionMiddleware())
    dp.update.outer_middleware(ChatLoggerMiddleware(logger=logger))

    # Routers
    dp.include_router(start.router)
    dp.include_router(panel.router)
    dp.include_router(statistics.router)
    dp.include_router(ads.router)
    dp.include_router(server.router)

    return bot, dp


async def startup(bot_obj: Bot, dp: Dispatcher):
    """Initialize external services (idempotent where possible)."""
    try:
        await RedisManager.init()
    except Exception:
        logger.exception("Redis init failed")

    try:
        await init_db()
    except Exception:
        logger.exception("init_db failed")

    logger.info("startup completed")


async def shutdown(bot_obj: Bot, dp: Dispatcher):
    """Gracefully close resources in a safe order; best-effort, with timeouts."""
    logger.info("shutdown started")

    # 1) stop dispatcher storage
    storage = getattr(dp, "storage", None)
    if storage is not None:
        try:
            await _close_with_timeout(storage.close(), "dp.storage.close()")
        except Exception:
            logger.exception("dp.storage.close failed")

    # 2) close bot HTTP session (aiohttp)
    if getattr(bot_obj, "session", None) is not None:
        try:
            await _close_with_timeout(bot_obj.session.close(), "bot.session.close()")
        except Exception:
            logger.exception("bot.session.close failed")

    # 3) close RedisManager
    try:
        await _close_with_timeout(RedisManager.close(), "RedisManager.close()")
    except Exception:
        logger.exception("RedisManager.close failed")

    # 4) dispose DB engine
    try:
        await _close_with_timeout(dispose_db(), "dispose_db()")
    except Exception:
        logger.exception("dispose_db failed")

    logger.info("shutdown finished")


async def run() -> None:
    bot_obj, dp = await create_bot_and_dp()

    # Ensure we always attempt shutdown even if errors / signals occur.
    polling_task: Optional[asyncio.Task] = None

    try:
        # start external services
        await startup(bot_obj, dp)

        # delete webhook (best-effort)
        try:
            await bot_obj.delete_webhook(drop_pending_updates=True)
        except Exception:
            logger.exception("delete_webhook() failed (continuing)")

        # prepare graceful stop event via signals
        loop = asyncio.get_running_loop()
        stop_event = asyncio.Event()

        def _on_signal():
            logger.info("stop signal received")
            stop_event.set()

        for s in (signal.SIGINT, signal.SIGTERM):
            try:
                loop.add_signal_handler(s, _on_signal)
            except NotImplementedError:
                # Windows: add_signal_handler may not be available
                pass

        # start polling
        polling_task = asyncio.create_task(
            dp.start_polling(bot_obj, allowed_updates=dp.resolve_used_update_types())
        )
        logger.info("polling started")

        # callback to log if polling ends unexpectedly
        def _on_poll_done(t: asyncio.Task):
            if t.cancelled():
                logger.info("polling task cancelled")
                return
            try:
                exc = t.exception()
            except asyncio.CancelledError:
                return
            if exc:
                logger.exception("polling task finished with exception: %s", exc)
            else:
                logger.info("polling task finished normally")

        polling_task.add_done_callback(_on_poll_done)

        # wait until stop_event is set (signal) OR polling task terminates
        done, _ = await asyncio.wait({polling_task, asyncio.create_task(stop_event.wait())},
                                     return_when=asyncio.FIRST_COMPLETED)

        # if stop_event triggered -> try graceful stop
        if stop_event.is_set():
            logger.info("initiating graceful stop of dispatcher")
            try:
                await asyncio.wait_for(dp.stop_polling(), timeout=STOP_TIMEOUT)
                logger.info("dp.stop_polling() finished")
            except asyncio.TimeoutError:
                logger.warning("dp.stop_polling() timed out, will cancel polling task")
            except Exception:
                logger.exception("dp.stop_polling() error")

    except Exception:
        # catch unexpected exceptions from the run loop and ensure shutdown
        logger.exception("Unhandled exception in run()")
        raise
    finally:
        # Ensure polling task is cancelled/awaited if still running
        if polling_task is not None and not polling_task.done():
            polling_task.cancel()
            try:
                await polling_task
            except asyncio.CancelledError:
                logger.info("polling task cancelled during shutdown")
            except Exception:
                logger.exception("awaiting cancelled polling task failed")

        # perform graceful shutdown of resources
        try:
            await shutdown(bot_obj, dp)
        except Exception:
            logger.exception("shutdown failed")


def main():
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt received; exiting")
    except Exception:
        logger.exception("Unhandled exception in main")
    finally:
        logger.info("process exited")


if __name__ == "__main__":
    main()
