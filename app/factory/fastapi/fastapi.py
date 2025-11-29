import time

from aiogram import Bot, Dispatcher
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from app.factory.fastapi import endpoints
from app.utils.time import set_start_time


def setup_fastapi(
        app: FastAPI,
        dispatcher: Dispatcher,
        bot: Bot,
        session_pool: async_sessionmaker[AsyncSession]
) -> FastAPI:
    app.state.dispatcher = dispatcher
    app.state.bot = bot
    app.state.shutdown_completed = False
    app.state.start_time = time.time()
    app.state.start_monotonic = time.monotonic()
    app.state.session_pool = session_pool
    set_start_time()
    app.include_router(endpoints.router)
    for key, value in dispatcher.workflow_data.items():
        setattr(app.state, key, value)
    return app
