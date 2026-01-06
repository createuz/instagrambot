from aiogram import Bot, Dispatcher
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from app.bot.telegram import create_bot, create_dispatcher
from app.utils.config import AppConfig
from app.utils.config.app_config import create_app_config
from app.db.session import create_session_pool
from app.api.lifecycle.app import run_polling, run_webhook
from app.utils.logging import setup_logger


def main() -> None:
    setup_logger()
    config: AppConfig = create_app_config()
    bot: Bot = create_bot(config=config)
    session_pool: async_sessionmaker[AsyncSession] = create_session_pool(config=config)
    dispatcher: Dispatcher = create_dispatcher(config=config, session_pool=session_pool)
    if config.telegram.use_webhook:
        return run_webhook(dispatcher=dispatcher, bot=bot, session_pool=session_pool, config=config)
    return run_polling(dispatcher=dispatcher, bot=bot, session_pool=session_pool, config=config)


if __name__ == "__main__":
    main()
