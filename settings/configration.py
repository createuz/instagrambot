import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from dotenv import load_dotenv

from .middlewares import ThrottlingMiddleware

load_dotenv()


class Config:
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    BOT_USERNAME = os.getenv("BOT_USERNAME")
    START_USER = os.getenv('START_USER')
    START_GROUP = os.getenv('START_GROUP')
    DB_URL = os.getenv('DB_URL')
    REDIS_URL = os.getenv('REDIS_URL')
    API_V1 = os.getenv("API_V1")
    API_V2 = os.getenv("API_V2")
    API_V3 = os.getenv("API_V3")
    API_V4 = os.getenv("API_V4")
    API_DL = os.getenv("API_DL")
    API_LIST = [API_V1, API_V2, API_V3, API_V4]


config = Config()
main_caption = f"<a href='{config.START_USER}'>{config.BOT_USERNAME}</a> l "
bot = Bot(token=config.BOT_TOKEN, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(ThrottlingMiddleware())
ADMINS = [5383531061, 6140152652]
logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)
