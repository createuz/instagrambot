# from states import LanguageSelection
# from db import *
# from keyboards import *
# from aiogram.utils import exceptions
#
#
# #
# #
# # @dp.message_handler(commands=['add_channel'], chat_id=ADMINS)
# # async def add_channel(message: types.Message):
# #     try:
# #         channel_id = message.text.split()[1]
# #         channel_info = await bot.get_chat(channel_id)
# #
# #         if not channel_info:
# #             await bot.send_message(chat_id=message.chat.id, text="Kanal topilmadi")
# #             return
# #
# #         async with engine.begin() as session:
# #             channel = [{
# #                 'chat_id': channel_info.id,
# #                 'title': channel_info.title,
# #                 'username': channel_info.username,
# #                 'invite_link': channel_info.invite_link}
# #             ]
# #             await session.execute(insert(Channel).values(channel))
# #         await bot.send_message(chat_id=message.chat.id, text="Kanal botga qo'shildi")
# #     except Exception as e:
# #         logger.exception("Error while sending broadcast message: %s", e)
# #         await message.answer('Kanal mavjud emas!')
# #         return
# #
# #
# # @dp.message_handler(commands=['remove_channel'], chat_id=ADMINS)
# # async def remove_channel(message: types.Message):
# #     try:
# #         channel_id = message.text.split()[1]
# #         async with engine.begin() as session:
# #             result = await session.execute(select(Channel).where(Channel.chat_id.ilike(channel_id)))
# #             channel = result.fetchone()
# #
# #             if not channel:
# #                 await bot.send_message(chat_id=message.chat.id, text="Kanal topilmadi")
# #                 return
# #             session.delete(channel)
# #         await bot.send_message(chat_id=message.chat.id, text="Kanal botdan o'chirildi")
# #     except Exception as e:
# #         logger.exception("Error while sending broadcast message: %s", e)
# #         await message.answer('Kanal mavjud emas!')
# #         return
# #
# #
# #
# # @dp.message_handler()
# # async def add_channel(message: types.Message):
# #     try:
# #         chat_id = message.chat.id
# #         channels = await get_all_channels()
# #         subscribed_channels = {channel.username for channel in channels
# #                                if await is_user_subscribed(chat_id, channel)}
# #
# #         if len(subscribed_channels) == len(channels):
# #             async with engine.begin() as session:
# #                 user = await session.scalar(select(User.language).where(User.chat_id.ilike(message.chat.id)))
# #                 if user:
# #                     language = user
# #                     await bot.send_message(chat_id, text=select_dict[language], reply_markup=keyboard_group[language],
# #                                            disable_web_page_preview=True, parse_mode='HTML')
# #                 else:
# #                     await bot.send_message(chat_id, text=choose_button, reply_markup=language_keyboard)
# #                     await LanguageSelection.select_language.set()
# #         else:
# #             buttons = [
# #                 InlineKeyboardButton(text=f'Channel №{i + 1}', url=f"https://t.me/{channel.username}")
# #                 for i, channel in enumerate(channels)
# #             ]
# #             check = InlineKeyboardButton(text='✅ Tasdiqlash', callback_data="check_subscription")
# #
# #             keyboard = InlineKeyboardMarkup(row_width=1)
# #             keyboard.add(*buttons)
# #             keyboard.add(check)
# #
# #             await bot.send_message(chat_id, "❗️Botdan foydalanish uchun quyidagi kanallarimizga obuna bo'ling 👇",
# #                                    reply_markup=keyboard)
# #     except Exception as e:
# #         logger.exception("Error while sending broadcast message: %s", e)
# #         return
# #
# #
# # async def is_user_subscribed(chat_id: int, channel: Channel) -> bool:
# #     try:
# #         member = await bot.get_chat_member(chat_id=channel.chat_id, user_id=chat_id)
# #         return member.is_chat_member()
# #     except exceptions.ChatNotFound:
# #         return False
# #
# #
# # @dp.callback_query_handler(lambda c: c.data == 'check_subscription')
# # async def check_subscription(call: types.CallbackQuery):
# #     try:
# #         chat_id = call.from_user.id
# #         channels = await get_all_channels()
# #         subscribed_channels = {channel.username for channel in channels
# #                                if await is_user_subscribed(chat_id, channel)}
# #         if len(subscribed_channels) == len(channels):
# #             await bot.answer_callback_query(call.id)
# #             callback_id = call.message.message_id
# #             async with engine.begin() as session:
# #                 user = await session.scalar(select(User.language).where(User.chat_id.ilike(chat_id)))
# #                 if user:
# #                     language = user
# #                     await bot.edit_message_text(chat_id=chat_id, message_id=callback_id, text=select_dict[language],
# #                                                 reply_markup=keyboard_group[language],
# #                                                 disable_web_page_preview=True)
# #                 else:
# #                     await bot.edit_message_text(chat_id=chat_id, message_id=callback_id, text=choose_button,
# #                                                 reply_markup=language_keyboard)
# #                     await LanguageSelection.select_language.set()
# #         else:
# #             await bot.answer_callback_query(call.id)
# #             callback_id = call.message.message_id
# #             buttons = [
# #                 InlineKeyboardButton(text=f'Channel №{i + 1}', url=f"https://t.me/{channel.username}")
# #                 for i, channel in enumerate(channels)
# #             ]
# #
# #             check = InlineKeyboardButton(text='✅ Tasdiqlash', callback_data="check_subscription")
# #
# #             keyboard = InlineKeyboardMarkup(row_width=1)
# #             keyboard.add(*buttons)
# #             keyboard.add(check)
# #             await bot.edit_message_text(chat_id, message_id=callback_id,
# #                                         text="❗️Botdan foydalanish uchun quyidagi kanallarimizga obuna bo'ling 👇",
# #                                         reply_markup=keyboard)
# #     except Exception as e:
# #         logger.exception("Error while sending broadcast message: %s", e)
# #         return
#
#
# @dp.message_handler(commands=['add_channel'], chat_id=ADMINS)
# async def add_channel(message: types.Message):
#     try:
#         channel_id = message.text.split()[1]
#         channel_info = await bot.get_chat(channel_id)
#
#         if not channel_info:
#             await bot.send_message(chat_id=message.chat.id, text="Kanal topilmadi")
#             return
#
#         async with engine.begin() as session:
#             channel = [{
#                 'chat_id': channel_info.id,
#                 'title': channel_info.title,
#                 'username': channel_info.username,
#                 'invite_link': channel_info.invite_link}
#             ]
#             await session.execute(insert(Channel).values(channel))
#         await bot.send_message(chat_id=message.chat.id, text="Kanal botga qo'shildi")
#     except Exception as e:
#         logger.exception("Error while adding a channel: %s", e)
#         await message.answer('Kanal mavjud emas!')
#         return
#
#
# @dp.message_handler(commands=['remove_channel'], chat_id=ADMINS)
# async def remove_channel(message: types.Message):
#     try:
#         channel_id = message.text.split()[1]
#         async with engine.begin() as session:
#             result = await session.execute(select(Channel).where(Channel.chat_id.ilike(channel_id)))
#             channel = result.fetchone()
#
#             if not channel:
#                 await bot.send_message(chat_id=message.chat.id, text="Kanal topilmadi")
#                 return
#             session.delete(channel)
#         await bot.send_message(chat_id=message.chat.id, text="Kanal botdan o'chirildi")
#     except Exception as e:
#         logger.exception("Error while removing a channel: %s", e)
#         await message.answer('Kanal mavjud emas!')
#         return
#
#
# @dp.message_handler()
# async def add_channel(message: types.Message):
#     try:
#         chat_id = message.chat.id
#         channels = await get_all_channels()
#         subscribed_channels = {channel.username for channel in channels
#                                if await is_user_subscribed(chat_id, channel)}
#
#         if len(subscribed_channels) == len(channels):
#             # User is already subscribed to all channels
#             return True
#         else:
#             buttons = [
#                 InlineKeyboardButton(text=f'Channel №{i + 1}', url=f"https://t.me/{channel.username}")
#                 for i, channel in enumerate(channels)
#             ]
#             check = InlineKeyboardButton(text='✅ Tasdiqlash', callback_data="check_subscription")
#
#             keyboard = InlineKeyboardMarkup(row_width=1)
#             keyboard.add(*buttons)
#             keyboard.add(check)
#
#             await bot.send_message(chat_id, "❗️Botdan foydalanish uchun quyidagi kanallarimizga obuna bo'ling 👇",
#                                    reply_markup=keyboard)
#     except Exception as e:
#         logger.exception("Error while sending broadcast message: %s", e)
#         return
#
#
# @dp.callback_query_handler(lambda c: c.data == 'check_subscription')
# async def check_subscription(call: types.CallbackQuery):
#     try:
#         chat_id = call.message.chat.id
#         channels = await get_all_channels()
#         subscribed_channels = {channel.username for channel in channels
#                                if await is_user_subscribed(chat_id, channel)}
#
#         if len(subscribed_channels) == len(channels):
#             await bot
#
#             return
#         else:
#             buttons = [
#                 InlineKeyboardButton(text=f'Channel №{i + 1}', url=f"https://t.me/{channel.username}")
#                 for i, channel in enumerate(channels)
#             ]
#             check = InlineKeyboardButton(text='✅ Tasdiqlash', callback_data="check_subscription")
#             keyboard = InlineKeyboardMarkup(row_width=2)
#             keyboard.add(*buttons)
#             keyboard.add(check)
#             await bot.send_message(chat_id, "❗️Botdan foydalanish uchun quyidagi"
#                                             " kanallarimizga obuna bo'ling 👇",
#                                    reply_markup=keyboard)
#     except Exception as e:
#         logger.exception("Error while sending broadcast message: %s", e)
#         return
#
