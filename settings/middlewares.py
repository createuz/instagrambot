from aiogram import types, Dispatcher
from aiogram.dispatcher import DEFAULT_RATE_LIMIT
from aiogram.dispatcher.handler import CancelHandler, current_handler
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.utils.exceptions import Throttled


def rate_limit(limit: int, key=None):
    """
    Decorator for configuring rate limit and key in different download.

    :param limit:
    :param key:
    :return:
    """

    def decorator(func):
        setattr(func, 'throttling_rate_limit', limit)
        if key:
            setattr(func, 'throttling_key', key)
        return func

    return decorator


class ThrottlingMiddleware(BaseMiddleware):
    """
    Simple middleware
    """

    def __init__(self, limit=DEFAULT_RATE_LIMIT, key_prefix='antiflood_'):
        self.rate_limit = limit
        self.prefix = key_prefix
        super(ThrottlingMiddleware, self).__init__()

    async def on_process_message(self, message: types.Message, data: dict):
        handler = current_handler.get()
        dispatcher = Dispatcher.get_current()
        if handler:
            limit = getattr(handler, "throttling_rate_limit", self.rate_limit)
            key = getattr(handler, "throttling_key", f"{self.prefix}_{handler.__name__}")
        else:
            limit = self.rate_limit
            key = f"{self.prefix}_message"
        try:
            await dispatcher.throttle(key, rate=limit)
        except Throttled as t:
            await self.message_throttled(message, t)
            raise CancelHandler()

    async def message_throttled(self, message: types.Message, throttled: Throttled):
        if throttled.exceeded_count <= 2:
            await message.reply("‼️ Too many requests!")

# from aiogram.dispatcher.handler import current_handler, CancelHandler
# from aiogram import types, Dispatcher
# from aiogram.utils.exceptions import Throttled
# import asyncio
#
#
# class ThrottlingMiddleware(BaseMiddleware):
#     def __init__(self, limit=2, timeout=2, max_warnings=5, ban_time=3600, key_prefix='antiflood_'):
#         """
#
#         :param limit:
#         :param timeout:
#         :param max_warnings:
#         :param ban_time:
#         :param key_prefix:
#         """
#         super().__init__()
#         self.rate_limit = limit
#         self.timeout = timeout
#         self.max_warnings = max_warnings
#         self.ban_time = ban_time
#         self.prefix = key_prefix
#         self.user_warnings = {}
#
#     async def on_pre_process_message(self, message: types.Message, data: dict):
#         handler = current_handler.get()
#         dispatcher = Dispatcher.get_current()
#         if handler:
#             limit = getattr(handler, "throttling_rate_limit", self.rate_limit)
#             key = getattr(handler, "throttling_key", f"{self.prefix}_{handler.__name__}")
#         else:
#             limit = self.rate_limit
#             key = f"{self.prefix}_message"
#
#         user_id = message.from_user.id
#
#         if user_id not in self.user_warnings:
#             self.user_warnings[user_id] = 0
#
#         if self.user_warnings[user_id] >= self.max_warnings:
#             await message.answer("Siz qoidaga zid harakatlarni amalga oshirmoqdasiz. "
#                                  "Agar bu holatni bir necha marotaba takrorlasangiz, "
#                                  "sizning xizmatdan bloklanganiz va boshqa xabarlariga javob berilmaydi!")
#             await asyncio.sleep(self.ban_time)
#             raise CancelHandler()
#         try:
#             await dispatcher.throttle(key, rate=limit)
#         except Throttled as t:
#             self.user_warnings[user_id] += 1
#             await message.answer("Siz so'rov tezligining limitidan oshdingiz shu sababli 10 sekund kutish rejimidasiz!")
#             await asyncio.sleep(self.timeout)
#         return
