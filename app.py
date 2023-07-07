from aiogram.utils.executor import start_webhook
from handlers import *
from misc import on_startup


async def main():
    db.init()
    logging.info("Starting bot polling...")
    await on_startup(dp)
    await db.create_all()
    await dp.start_polling()


if __name__ == '__main__':
    asyncio.run(main())
