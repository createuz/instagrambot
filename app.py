from handlers import *


async def main():
    await db.init()
    await cache._redis.ping()
    logger.info("""
                ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
                ┃      Starting bot polling...        ┃
                ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
    """)
    await dp.bot.send_message(
        chat_id=ADMINS[0],
        text=f"<b>✅  Bot ishga tushdi</b>",
        reply_markup=InlineKeyboardMarkup(row_width=1).add(
            InlineKeyboardButton(text='🔻', callback_data=f"bekor_qilish"))
    )
    await dp.start_polling()


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
