from handlers import *


async def main():
    db.init()
    logger.info("""
                ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
                ┃      Starting bot polling...        ┃
                ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
    """)
    del_help = InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton(text='🔻', callback_data=f"bekor_qilish"))
    await dp.bot.send_message(ADMINS[0], f"<b>⚡️ Bot ishga tushdi!</b>", reply_markup=del_help)
    await db.create_all()
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
WorkingDirectory=/var/www/InstagramBot
ExecStart=/var/www/InstagramBot/venv/bin/python3.11 app.py
[Install]
WantedBy=multi-user.target
'''
