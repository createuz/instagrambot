import os, logging
from dotenv import load_dotenv
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from data.middlewares import ThrottlingMiddleware

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
INSTA_API = os.getenv("INSTA_API")
ADMINS = [5383531061, 6140152652]
DB_URL = os.getenv('DB_URL')
BOT_URL = os.getenv('BOT_URL')
BOT_START = os.getenv('BOT_START')
ADMIN_PASSWORD_HASH = os.getenv('ADMIN_PASSWORD_HASH')
main_caption = f"<a href='{BOT_START}'>𝐈𝐧𝐬𝐭𝐢𝐧𝐁𝐨𝐭</a> | "

logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
time_now = datetime.now()
current_time = time_now.strftime("%H:%M:%S")
dp.middleware.setup(ThrottlingMiddleware())
