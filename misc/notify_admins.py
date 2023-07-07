import logging

from aiogram import Dispatcher
from data import ADMINS


async def on_startup(dp: Dispatcher):
    try:
        await dp.bot.send_message(ADMINS, "⚙ Bot ishga tushdi")
    except Exception as err:
        logging.exception(err)
