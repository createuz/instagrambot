# import asyncio
# import time
# import asyncio
# import time
# from asyncio.log import logger
from typing import Union

from data import ADMINS
from databasedb.models import User, Group
from keyboards import menu_kb
from loader import bot


# def format_time(elapsed_time):
#     hours, rem = divmod(elapsed_time, 3600)
#     minutes, seconds = divmod(rem, 60)
#     return f"{int(hours):02d} : {int(minutes):02d} : {int(seconds):02d}"
#
#
# async def send_message_all(chat_id, text=None, video=None, photo=None, caption=None, keyboard=None):
#     try:
#         if text:
#             await bot.send_message(chat_id=chat_id, text=text, reply_markup=keyboard,
#                                    disable_web_page_preview=True)
#         if video:
#             await bot.send_video(chat_id=chat_id, video=video, caption=caption, reply_markup=keyboard,
#                                  disable_web_page_preview=True)
#         if photo:
#             await bot.send_photo(chat_id=chat_id, photo=photo, caption=caption, reply_markup=keyboard,
#                                  disable_web_page_preview=True)
#         return True
#     except Exception as e:
#         logger.exception("Xabarni yuborishda xatolik: %s", e)
#         return False
#
#
# async def send_messages_to_users(user_ids: list, text=None, video=None, photo=None, caption=None, keyboard=None):
#     active_count = 0
#     no_active_count = 0
#     for user_id in user_ids:
#         if await send_message_all(user_id, text=text, video=video, photo=photo, caption=caption, keyboard=keyboard):
#             active_count += 1
#         else:
#             no_active_count += 1
#         await asyncio.sleep(.05)
#     return active_count, no_active_count
#
#
# async def send_messages_to_groups(group_ids: list, text=None, video=None, photo=None, caption=None, keyboard=None):
#     active_count = 0
#     no_active_count = 0
#     for group_id in group_ids:
#         if await send_message_all(group_id, text=text, video=video, photo=photo, caption=caption, keyboard=keyboard):
#             active_count += 1
#         else:
#             no_active_count += 1
#         await asyncio.sleep(.05)
#     return active_count, no_active_count
#
#
# try:
#     start_time = time.time()
#
#     all_user_ids = await User.get_all_user()
#     active_users, no_active_users = await send_messages_to_users(all_user_ids, 'Assalomu alaykum')
#
#     all_group_ids = await Group.get_all_group()
#     active_groups, no_active_groups = await send_messages_to_groups(all_group_ids, 'Assalomu alaykum', keyboard=menu_kb)
#
#     elapsed_time = time.time() - start_time
#
#     date = format_time(elapsed_time)
#
#     msg = (
#         f"Barcha foydalanuvchilar: {len(all_user_ids)}\n"
#         f"Active foydalanuvchilar: {active_users}\n"
#         f"No Active foydalanuvchilar: {no_active_users}\n"
#         f"Barcha guruhlar: {len(all_group_ids)}\n"
#         f"Active guruhlar: {active_groups}\n"
#         f"No Active guruhlar: {no_active_groups}\n"
#         f"Jami vaqt: {date}"
#     )
#     await bot.send_message(ADMINS, text=msg)
#
# except Exception as e:
#     logger.exception("Xabarni yuborishda xatolik: %s", e)
#     await bot.send_message(ADMINS, 'Xabarni yuborishda xatolik yuz berdi.')
