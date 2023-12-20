from handlers import *


async def main():
    db.init()
    logger.info("....... Starting bot polling ........")
    await on_startup(dp)
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



Assolumu Alaykum! 

Qo‘shiqni topib berishim uchun, 
quyidagilardan birini yuboring!

• Qo‘shiq nomi yoki ijrochi ismi
• Qo‘shiq matni
• Ovozli xabar
• Video
• Audio
• Video xabar
• Instagram link
• Tik Tok link


'''
