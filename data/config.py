import os
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
INSTA_API = os.getenv("INSTA_API")
ADMINS = os.getenv("ADMINS")
DB_URL = os.getenv('DB_URL')
BOT_URL = os.getenv('BOT_URL')
BOT_START = os.getenv('BOT_START')
ADMIN_PASSWORD_HASH = os.getenv('ADMIN_PASSWORD_HASH')
main_caption = f"<a href='{BOT_START}'>𝐈𝐧𝐬𝐭𝐢𝐧𝐁𝐨𝐭</a> | "
