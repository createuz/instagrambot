from db import cache
from handlers import *
from keyboards import start_bot


async def main():
    await db.init()
    await cache.redis.ping()
    await dp.bot.send_message(chat_id=ADMINS[0], text=f"<b>✅  Bot ishga tushdi</b>", reply_markup=bekor_qilish_kb)
    await dp.start_polling()
    logger.info(start_bot)

if __name__ == '__main__':
    asyncio.run(main())

'''     
[Unit]
Description=gunicorn daemon
After=network.target
[Service]
User=root
Group=www-data
WorkingDirectory=/var/www/instagrambot
ExecStart=/var/www/instagrambot/venv/bin/python3.11 app.py
[Install]
WantedBy=multi-user.target
'''
