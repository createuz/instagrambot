import os, logging
from dotenv import load_dotenv
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from data.middlewares import ThrottlingMiddleware

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
INSTA_API1 = os.getenv("INSTA_API1")
INSTA_API2 = os.getenv("INSTA_API2")
INSTA_API3 = os.getenv("INSTA_API3")
INSTA_API4 = os.getenv("INSTA_API4")
ADMINS = [5383531061, 6140152652]
DB_URL = os.getenv('DB_URL')
BOT_URL = os.getenv('BOT_URL')
BOT_START = os.getenv('BOT_START')
ADMIN_PASSWORD_HASH = os.getenv('ADMIN_PASSWORD_HASH')
main_caption = f"<a href='{BOT_START}'>instavsbot</a> | "

logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(ThrottlingMiddleware())

