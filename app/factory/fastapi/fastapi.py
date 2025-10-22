import time

from aiogram import Bot, Dispatcher
from fastapi import FastAPI

from app.factory.fastapi import endpoints
from app.utils.time import set_start_time


def setup_fastapi(app: FastAPI, dispatcher: Dispatcher, bot: Bot) -> FastAPI:
    app.state.dispatcher = dispatcher
    app.state.bot = bot
    app.state.shutdown_completed = False
    app.state.start_time = time.time()
    app.state.start_monotonic = time.monotonic()
    set_start_time()
    app.include_router(endpoints.router)
    for key, value in dispatcher.workflow_data.items():
        setattr(app.state, key, value)
    return app
