import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot token
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Other APIs
INSTA_API = os.getenv("INSTA_API")

# Admin IDs
ADMINS = os.getenv("ADMINS")

# Database URL
DB_URL = os.getenv('DB_URL')

# Bot URL
BOT_URL = os.getenv('BOT_URL')

# Bot Start URL
BOT_START = os.getenv('BOT_START')

# hash
ADMIN_PASSWORD_HASH = os.getenv('ADMIN_PASSWORD_HASH')

# Caption
main_caption = f"<a href='{BOT_START}'>𝐈𝐧𝐬𝐭𝐢𝐧𝐁𝐨𝐭</a> | "

WEBHOOK_HOST = os.getenv('WEBHOOK_HOST')

WEBHOOK_PORT = os.getenv('WEBHOOK_PORT')