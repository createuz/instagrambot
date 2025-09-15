# main.py
import asyncio
import signal

from redis.asyncio import Redis

from app.bot.handlers.admins import panel_router
from app.bot.handlers.users import start, callbacks
from app.bot.middlewares.db_middleware import DBSessionMiddleware
from app.bot.middlewares.request_id_middleware import RequestIDMiddleware
from app.bot.middlewares.update_middleware import ChatLoggerMiddleware
from app.bot.utils import get_dispatcher, get_redis_storage
from app.core import conf
from app.core.config import bot
from app.core.logger import get_logger
from app.db.services.redis_manager import RedisManager
from app.db.sessions.session import init_db, dispose_db

logger = get_logger()

async def create_bot_and_dp():
    storage = get_redis_storage(redis=Redis.from_url(conf.redis.url_or_build()))
    dp = get_dispatcher(storage=storage)
    dp.update.outer_middleware(RequestIDMiddleware())
    dp.update.outer_middleware(DBSessionMiddleware())
    dp.update.outer_middleware(ChatLoggerMiddleware(logger=logger))
    dp.include_router(start.router)
    dp.include_router(callbacks.router)
    dp.include_router(panel_router)
    return bot, dp


async def startup(bot, dp):
    await RedisManager.init()
    await init_db()
    logger.info("startup finished")


async def shutdown(bot, dp):
    try:
        await dp.storage.close()
    except Exception:
        logger.exception("closing storage failed")
    try:
        await bot.session.close()
    except Exception:
        logger.exception("closing bot session failed")
    await RedisManager.close()
    await dispose_db()
    logger.info("shutdown finished")


async def run_polling():
    bot, dp = await create_bot_and_dp()
    await startup(bot, dp)

    loop = asyncio.get_running_loop()
    stop_event = asyncio.Event()

    def _on_sig():
        logger.info("signal received")
        stop_event.set()

    for s in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(s, _on_sig)
        except NotImplementedError:
            pass
    await bot.delete_webhook(drop_pending_updates=True)
    polling_task = asyncio.create_task(dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types()))
    stop_task = asyncio.create_task(stop_event.wait())
    done, pending = await asyncio.wait([polling_task, stop_task], return_when=asyncio.FIRST_COMPLETED)

    if not polling_task.done():
        try:
            await dp.stop_polling()
        except Exception:
            logger.exception("stop polling failed")

    for t in (polling_task, stop_task):
        if not t.done():
            t.cancel()
            try:
                await t
            except asyncio.CancelledError:
                pass

    await shutdown(bot, dp)


if __name__ == "__main__":
    try:
        asyncio.run(run_polling())
    except KeyboardInterrupt:
        pass
