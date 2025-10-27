# main.py (recommended minimal, clear, production-ready)
import asyncio
import signal
from typing import Optional, Tuple

from aiogram import Bot, Dispatcher
from redis.asyncio import Redis

from old.bot.handlers.admins import panel, statistics, ads, server
from old.bot.handlers.users import start
from old.bot.middlewares.db_middleware import DBSessionMiddleware
from old.bot.middlewares.update_middleware import ChatLoggerMiddleware
from old.bot.utils import get_dispatcher, get_redis_storage
from old.core import conf
from old.core.config import bot as global_bot
from old.core.logger import get_logger
from old.db.services.redis_manager import RedisManager
from old.db.sessions.session import init_db, dispose_db

logger = get_logger()

# Tunable
STOP_TIMEOUT = 20.0
CLOSE_TIMEOUT = 10.0


async def _close_with_timeout(coro, name: str, timeout: float = CLOSE_TIMEOUT):
    try:
        return await asyncio.wait_for(coro, timeout=timeout)
    except asyncio.TimeoutError:
        logger.warning("%s did not finish within %.1fs", name, timeout)
    except Exception:
        logger.exception("Error while closing %s", name)


async def create_bot_and_dp() -> Tuple[Bot, Dispatcher]:
    """
    Create Bot and Dispatcher in a clear, deterministic way.
    Uses global_bot if set in old.core.config, otherwise creates from conf.bot.token.
    """
    bot_instance: Optional[Bot] = global_bot
    if bot_instance is None:
        token = getattr(conf, "bot", None) and getattr(conf.bot, "token", None)
        if not token:
            raise RuntimeError("Bot instance not configured and conf.bot.token missing")
        bot_instance = Bot(token=token)

    # storage (Redis-backed or fallback)
    storage = get_redis_storage(redis=Redis.from_url(conf.redis.url_or_build()))

    # create dispatcher (adapt to your util's signature)
    try:
        dp: Dispatcher = get_dispatcher(storage=storage)
    except TypeError:
        dp = get_dispatcher(bot_instance, storage)

    # register middlewares + routers
    dp.update.outer_middleware(DBSessionMiddleware())
    dp.update.outer_middleware(ChatLoggerMiddleware(logger=logger))

    dp.include_router(start.router)
    dp.include_router(panel.router)
    dp.include_router(statistics.router)
    dp.include_router(ads.router)
    dp.include_router(server.router)

    return bot_instance, dp


async def startup(bot_obj: Bot, dp: Dispatcher):
    """
    Init external services. Lower-level functions (RedisManager.init, init_db)
    should already log their success and be idempotent.
    """
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
    logger.info("shutdown started")

    # close dp storage
    storage = getattr(dp, "storage", None)
    if storage is not None:
        await _close_with_timeout(storage.close(), "dp.storage.close()")

    # close bot http session
    if getattr(bot_obj, "session", None) is not None:
        await _close_with_timeout(bot_obj.session.close(), "bot.session.close()")

    # close RedisManager
    await _close_with_timeout(RedisManager.close(), "RedisManager.close()")

    # dispose DB engine
    await _close_with_timeout(dispose_db(), "dispose_db()")

    logger.info("shutdown finished")


async def run():
    bot_obj, dp = await create_bot_and_dp()

    # manage lifecycle + graceful stop
    polling_task: Optional[asyncio.Task] = None
    stop_event = asyncio.Event()

    def _on_signal():
        logger.info("signal received - stopping")
        stop_event.set()

    loop = asyncio.get_running_loop()
    for s in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(s, _on_signal)
        except NotImplementedError:
            pass  # Windows

    try:
        await startup(bot_obj, dp)

        # ensure no webhook left
        try:
            await bot_obj.delete_webhook(drop_pending_updates=True)
        except Exception:
            logger.debug("delete_webhook failed (continuing)")

        # Supervisor loop: if start_polling fails (network), we can restart with backoff.
        async def polling_supervisor():
            backoff = 1.0
            max_backoff = 60.0
            while not stop_event.is_set():
                try:
                    logger.info("starting polling")
                    await dp.start_polling(
                        bot_obj, allowed_updates=dp.resolve_used_update_types()
                    )
                    # start_polling returned normally -> break
                    logger.info("dp.start_polling returned (normal exit)")
                    return
                except asyncio.CancelledError:
                    raise
                except Exception as e:
                    logger.warning(
                        "Polling failed: %s. restarting in %.1fs", e, backoff
                    )
                    await asyncio.wait(
                        [
                            asyncio.create_task(stop_event.wait()),
                            asyncio.create_task(asyncio.sleep(backoff)),
                        ],
                        return_when=asyncio.FIRST_COMPLETED,
                    )
                    if stop_event.is_set():
                        return
                    backoff = min(backoff * 2, max_backoff)

        polling_task = asyncio.create_task(polling_supervisor())

        # wait for stop_event
        await stop_event.wait()
        logger.info("stop_event set, initiating graceful shutdown")

        # ask dispatcher to stop
        try:
            await asyncio.wait_for(dp.stop_polling(), timeout=STOP_TIMEOUT)
            logger.info("dp.stop_polling finished")
        except asyncio.TimeoutError:
            logger.warning("dp.stop_polling timed out")
        except Exception:
            logger.exception("dp.stop_polling error")

    except Exception:
        logger.exception("Unhandled error in run()")
        raise
    finally:
        # cancel/await polling task
        if polling_task and not polling_task.done():
            polling_task.cancel()
            try:
                await polling_task
            except asyncio.CancelledError:
                logger.info("polling task cancelled during shutdown")
            except Exception:
                logger.exception("awaiting cancelled polling task failed")

        # shutdown resources
        await shutdown(bot_obj, dp)


def main():
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt received; exiting")
    except Exception:
        logger.exception("Unhandled exception in main()")
    finally:
        logger.info("process exited")


if __name__ == "__main__":
    main()
