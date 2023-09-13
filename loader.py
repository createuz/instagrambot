import logging, aiohttp, asyncio
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from sqlalchemy import Column, Integer, String, select, func, delete, insert
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import DeclarativeBase
from aiogram.dispatcher.filters import Text
import aiohttp, logging
from sqlalchemy import select, insert, update
from sqlalchemy.ext.asyncio import create_async_engine
from pyquery import PyQuery as pq
from sqlalchemy.dialects.postgresql.psycopg2 import logger
from asyncio.log import logger
from aiogram.dispatcher import FSMContext
from aiogram.types import ContentType
from data.config import *
from aiogram.types import InputMediaPhoto, InputMediaVideo
from sqlalchemy import JSON
from typing import List, Union, Any
import logging
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils import executor
import bcrypt
from middlewares import ThrottlingMiddleware

logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s',
                    level=logging.INFO,
                    # level=logging.DEBUG,
                    )
bot = Bot(token=BOT_TOKEN, parse_mode=types.ParseMode.MARKDOWN_V2)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
logging.basicConfig(level=logging.INFO)
time_now = datetime.now()
current_time = time_now.strftime("%H:%M:%S")
dp.middleware.setup(ThrottlingMiddleware())
