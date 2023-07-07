from aiogram.utils.executor import start_webhook
from handlers import *

logging.basicConfig(level=logging.INFO)
dp.middleware.setup(LoggingMiddleware())


async def on_startup(dp: Dispatcher):
    try:
        await bot.set_webhook(url=f"{WEBHOOK_HOST}/insta/bot")
        db.init()
        logging.info("Starting bot polling...")
        await db.create_all()
        await dp.bot.send_message(ADMINS, "⚙ Bot ishga tushdi")
    except Exception as err:
        logging.exception(err)


async def on_shutdown(dp: Dispatcher):
    logging.warning('Shutting down...')
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.storage.close()
    await dp.storage.wait_closed()
    logging.warning('Bye!')


if __name__ == '__main__':
    start_webhook(
        dispatcher=dp,
        webhook_path='/insta/bot',
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True,
        host='localhost',
        port=8080
    )

# async def main():
#     db.init()
#     logging.info("Starting bot polling...")
#     await on_startup(dp)
#     await db.create_all()
#     await dp.start_polling()
#
#
# if __name__ == '__main__':
#     asyncio.run(main())
