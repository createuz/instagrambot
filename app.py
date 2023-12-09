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
WorkingDirectory=/var/www/instagrambot
ExecStart=/var/www/instagrambot/venv/bin/python3.11 app.py

[Install]
WantedBy=multi-user.target



ExecStart=/var/www/instagrambot/venv/bin/gunicorn app:app -b 127.0.0.1:8000 --workers 3 --chdir=/var/www/instagrambot --preload --access-logfile /var/www/instagrambot/access.log --error-logfile /var/www/instagrambot/error.log --timeout 60 --static-map /static=/var/www/instagrambot/static
Restart=always

[Install]
WantedBy=multi-user.target


'''
