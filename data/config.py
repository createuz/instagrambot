import os, logging
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from data.middlewares import ThrottlingMiddleware

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
BOT_USERNAME = os.getenv("BOT_USERNAME")
INSTA_API1 = os.getenv("INSTA_API1")
INSTA_API2 = os.getenv("INSTA_API2")
INSTA_API3 = os.getenv("INSTA_API3")
INSTA_API4 = os.getenv("INSTA_API4")
INSTA_API_DL = os.getenv("INSTA_API_DL")
STORIES_API = os.getenv("INSTA_STORIES_API")
DB_URL = os.getenv('DB_URL')
REDIS_URL = "redis://localhost:6379/0"
BOT_URL = os.getenv('BOT_URL')
BOT_START = os.getenv('BOT_START')
INSTA_API_LIST = [INSTA_API1, INSTA_API2, INSTA_API3, INSTA_API4]
ADMINS = [5383531061, 6140152652]
main_caption = f"<a href='{BOT_START}'>{BOT_USERNAME}</a> l "
bot = Bot(token=BOT_TOKEN, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(ThrottlingMiddleware())

logging.basicConfig(
    format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)
