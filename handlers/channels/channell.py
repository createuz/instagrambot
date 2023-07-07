# from states import LanguageSelection
#
# data = {"id": -1001837053122,
#         "title": "Python Developer",
#         "username": "tmpython", "type": "channel",
#         "active_usernames": ["tmpython"], "description": "contact: @tmcoderr",
#         "invite_link": "https://t.me/+jSAro0s3lRsyMDRi", "linked_chat_id": -1001511928335,
#         "photo": {"small_file_id": "AQADAgAD_sMxGzTD8UoACAIAAz67270W____djcjKbxOVuQvBA",
#                   "small_file_unique_id": "AQAD_sMxGzTD8UoAAQ",
#                   "big_file_id": "AQADAgAD_sMxGzTD8UoACAMAAz67270W____djcjKbxOVuQvBA",
#                   "big_file_unique_id": "AQAD_sMxGzTD8UoB"}}
#
# from aiogram.utils import exceptions
# # from databasedb import *
# # from keyboards import *
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
#         logger.exception("Error while sending broadcast message: %s", e)
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
#         logger.exception("Error while sending broadcast message: %s", e)
#         await message.answer('Kanal mavjud emas!')
#         return
#
#
# # @dp.message_handler()
# # async def add_channel(message: types.Message):
# #     try:
# #         user_id = message.from_user.id
# #         channels = await get_all_channels()
# #
# #         subscribed_channels = []
# #         for channel in channels:
# #             try:
# #                 member = await bot.get_chat_member(chat_id=channel.chat_id, user_id=user_id)
# #                 if member.is_chat_member():
# #                     subscribed_channels.append(channel.username)
# #             except exceptions.ChatNotFound:
# #                 pass
# #
# #         if len(subscribed_channels) == len(channels):
# #             async with engine.begin() as session:
# #                 user = await session.scalar(select(User.language).where(User.chat_id.ilike(message.chat.id)))
# #             if user:
# #                 language = user
# #                 await message.answer(text=select_dict[language], reply_markup=keyboard_group[language],
# #                                      disable_web_page_preview=True, parse_mode='HTML')
# #             else:
# #                 await message.answer(text=choose_button, reply_markup=language_keyboard)
# #                 await LanguageSelection.select_language.set()
# #         else:
# #             await bot.send_message(chat_id=message.chat.id,
# #                                    text="❗️Botdan foydalanish uchun quyidagi kanallarimizga obuna bo'ling 👇")
# #             buttons = [
# #                 InlineKeyboardButton(text=channel.title, url=f"https://t.me/{channel.username}")
# #                 for channel in channels
# #             ]
# #
# #             check = InlineKeyboardMarkup(row_width=1).add(
# #                 InlineKeyboardButton(text='✅ Tasdiqlash', callback_data="check_subscription"))
# #             keyboard = InlineKeyboardMarkup(row_width=1)
# #             keyboard.add(*buttons, check)
# #             await bot.send_message(message.chat.id, 'kanalga obuna boling', reply_markup=buttons)
# #     except Exception as e:
# #         logger.exception("Error while sending broadcast message: %s", e)
# #         return
#
#
# @dp.message_handler()
# async def add_channel(message: types.Message):
#     try:
#         chat_id = message.chat.id
#         channels = await get_all_channels()
#         subscribed_channels = {channel.username for channel in channels
#                                if await bot.get_chat_member(chat_id=channel.chat_id, user_id=chat_id).is_chat_member()}
#
#         if len(subscribed_channels) == len(channels):
#             async with engine.begin() as session:
#                 user = await session.scalar(select(User.language).where(User.chat_id.ilike(message.chat.id)))
#                 if user:
#                     language = user
#                     await bot.send_message(chat_id, text=select_dict[language], reply_markup=keyboard_group[language],
#                                            disable_web_page_preview=True, parse_mode='HTML')
#                 else:
#                     await bot.send_message(chat_id, text=choose_button, reply_markup=language_keyboard)
#                     await LanguageSelection.select_language.set()
#         else:
#             buttons = [
#                 InlineKeyboardButton(text=channel.title, url=f"https://t.me/{channel.username}")
#                 for channel in channels
#             ]
#
#             check = InlineKeyboardMarkup(row_width=1).add(
#                 InlineKeyboardButton(text='✅ Tasdiqlash', callback_data="check_subscription"))
#             keyboard = InlineKeyboardMarkup(row_width=1)
#             keyboard.add(*buttons, check)
#             await bot.send_message(chat_id,
#                                    text="❗️Botdan foydalanish uchun quyidagi kanallarimizga obuna bo'ling 👇",
#                                    reply_markup=keyboard)
#     except Exception as e:
#         logger.exception("Error while sending broadcast message: %s", e)
#         return
#
#
# @dp.callback_query_handler(lambda c: c.data == 'check_subscription')
# async def check_subscription(call: types.CallbackQuery):
#     try:
#         chat_id = call.from_user.id
#         channels = await get_all_channels()
#         subscribed_channels = {channel.username for channel in channels
#                                if await bot.get_chat_member(chat_id=channel.chat_id, user_id=chat_id).is_chat_member()}
#         if len(subscribed_channels) == len(channels):
#             await bot.answer_callback_query(call.id)
#             callback_id = call.message.message_id
#             async with engine.begin() as session:
#                 user = await session.scalar(select(User.language).where(User.chat_id.ilike(chat_id)))
#                 if user:
#                     language = user
#                     await bot.edit_message_text(chat_id, message_id=callback_id, text=select_dict[language],
#                                                 reply_markup=keyboard_group[language],
#                                                 disable_web_page_preview=True)
#                 else:
#                     await bot.edit_message_text(chat_id, message_id=callback_id, text=choose_button,
#                                                 reply_markup=language_keyboard)
#                     await LanguageSelection.select_language.set()
#         else:
#             buttons = [
#                 InlineKeyboardButton(text=channel.title, url=f"https://t.me/{channel.username}")
#                 for channel in channels
#             ]
#
#             check = InlineKeyboardMarkup(row_width=1).add(
#                 InlineKeyboardButton(text='✅ Tasdiqlash', callback_data="check_subscription"))
#             keyboard = InlineKeyboardMarkup(row_width=1)
#             keyboard.add(*buttons, check)
#             await bot.send_message(chat_id,
#                                    text="❗️Botdan foydalanish uchun quyidagi kanallarimizga obuna bo'ling 👇",
#                                    reply_markup=keyboard)
#     except Exception as e:
#         logger.exception("Error while sending broadcast message: %s", e)
#         return
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
# #
# # async def add_channel(message: types.Message):
# #     try:
# #         chat_id = message.chat.id
# #         channels = await get_all_channels()
# #         subscribed_channels = {channel.username for channel in channels
# #                                if await is_user_subscribed(chat_id, channel)}
# #
# #         if len(subscribed_channels) == len(channels):
# #             # User is already subscribed to all channels
# #             return True
# #         else:
# #             return False
# #     except Exception as e:
# #         logger.exception("Error while sending broadcast message: %s", e)
# #         return False
# #
# # @dp.callback_query_handler(lambda c: c.data == 'check_subscription')
# # async def check_subscription(call: types.CallbackQuery):
# #     try:
# #         chat_id = call.from_user.id
# #         channels = await get_all_channels()
# #         subscribed_channels = {channel.username for channel in channels
# #                                if await is_user_subscribed(chat_id, channel)}
# #         if len(subscribed_channels) == len(channels):
# #             return True
# #         else:
# #             return False
# #     except Exception as e:
# #         logger.exception("Error while checking subscription: %s", e)
# #         return False
# #
# #
# #
# # @dp.message_handler(regexp=r'https?:\/\/(www\.)?pin\.it\/\w+|https?:\/\/(www\.)?pinterest\.com\/pin\/\w+')
# # async def send_pinterest_all_media(message: types.Message):
# #     try:
# #         if add_channel(message) is not False:
# #             await message.delete()
# #             async with engine.begin() as conn:
# #                 language = await conn.scalar(select(User.language).where(User.chat_id.ilike(message.chat.id)))
# #                 video = await conn.scalar(select(PinterestDB.video_url).where(PinterestDB.video_id.ilike(message.text)))
# #                 if video:
# #                     if 'mp4' in video:
# #                         await bot.send_video(chat_id=message.chat.id, video=video,
# #                                              caption=f"{main_caption}{keyboard_saver[language]} 📥")
# #                     else:
# #                         await bot.send_photo(chat_id=message.chat.id, photo=video,
# #                                              caption=f"{main_caption}{keyboard_saver[language]} 📥")
# #                 else:
# #                     waiting_msg = await bot.send_message(chat_id=message.chat.id,
# #                                                          text=f"📥 {keyboard_waiting[language]}")
# #                     async with aiohttp.ClientSession() as session:
# #                         video_url = await pinterest_downloader(message.text, session=session)
# #                     if 'mp4' in video_url:
# #                         await waiting_msg.delete()
# #                         await bot.send_video(chat_id=message.chat.id, video=video_url,
# #                                              caption=f"{main_caption}{keyboard_saver[language]} 📥")
# #                     else:
# #                         await waiting_msg.delete()
# #                         await bot.send_photo(chat_id=message.chat.id, photo=video_url,
# #                                              caption=f"{main_caption}{keyboard_saver[language]} 📥")
# #                     await pinterest_db(message.text, video_url, conn)
# #
# #         if check_subscription() is not True:
# #             chat_id = message.chat.id
# #             channels = await get_all_channels()
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
# #                                reply_markup=keyboard)
# #     except Exception as e:
# #         logger.exception("Error while sending Instagram video: %s", e)
#
#
# # async def add_channel(message: types.Message):
# #     try:
# #         chat_id = message.chat.id
# #         channels = await get_all_channels()
# #         subscribed_channels = {channel.username for channel in channels
# #                                if await is_user_subscribed(chat_id, channel)}
# #
# #         if len(subscribed_channels) == len(channels):
# #             # User is already subscribed to all channels
# #             return True
# #         else:
# #             return False
# #     except Exception as e:
# #         logger.exception("Error while sending broadcast message: %s", e)
# #         return False
# #
# #
# # async def check_subscription(message: types.Message = None, call: types.CallbackQuery = None):
# #     if message is None and call is None:
# #         raise ValueError("Either 'call' or 'message' argument must be provided.")
# #
# #     chat_id = message.chat.id if message is not None else call.message.chat.id
# #     channels = await get_all_channels()
# #     buttons = [
# #         InlineKeyboardButton(text=f'Channel №{i + 1}', url=f"https://t.me/{channel.username}")
# #         for i, channel in enumerate(channels)
# #     ]
# #     check = InlineKeyboardButton(text='✅ Tasdiqlash', callback_data="check_subscription")
# #
# #     keyboard = InlineKeyboardMarkup(row_width=1)
# #     keyboard.add(*buttons)
# #     keyboard.add(check)
# #
# #     await bot.send_message(chat_id, "❗️Botdan foydalanish uchun quyidagi kanallarimizga obuna bo'ling 👇",
# #                            reply_markup=keyboard)
# #
# #
# # @dp.message_handler(regexp=r'https?:\/\/(www\.)?pin\.it\/\w+|https?:\/\/(www\.)?pinterest\.com\/pin\/\w+')
# # async def send_pinterest_all_media(message: types.Message = None, call: types.CallbackQuery = None):
# #     try:
# #         if message is not None and message.chat is not None:
# #             if await add_channel(message):
# #                 await message.delete()
# #                 async with engine.begin() as conn:
# #                     language = await conn.scalar(select(User.language).where(User.chat_id.ilike(message.chat.id)))
# #                     video = await conn.scalar(
# #                         select(PinterestDB.video_url).where(PinterestDB.video_id.ilike(message.text)))
# #                     if video:
# #                         if 'mp4' in video:
# #                             await bot.send_video(chat_id=message.chat.id, video=video,
# #                                                  caption=f"{main_caption}{keyboard_saver[language]} 📥")
# #                         else:
# #                             await bot.send_photo(chat_id=message.chat.id, photo=video,
# #                                                  caption=f"{main_caption}{keyboard_saver[language]} 📥")
# #                     else:
# #                         waiting_msg = await bot.send_message(chat_id=message.chat.id,
# #                                                              text=f"📥 {keyboard_waiting[language]}")
# #                         async with aiohttp.ClientSession() as session:
# #                             video_url = await pinterest_downloader(message.text, session=session)
# #                         if 'mp4' in video_url:
# #                             await waiting_msg.delete()
# #                             await bot.send_video(chat_id=message.chat.id, video=video_url,
# #                                                  caption=f"{main_caption}{keyboard_saver[language]} 📥")
# #                         else:
# #                             await waiting_msg.delete()
# #                             await bot.send_photo(chat_id=message.chat.id, photo=video_url,
# #                                                  caption=f"{main_caption}{keyboard_saver[language]} 📥")
# #                         await pinterest_db(message.text, video_url, conn)
# #
# #         elif call is not None and call.message is not None:
# #             if await add_channel(call.message):
# #                 await call.message.delete()
# #                 async with engine.begin() as conn:
# #                     language = await conn.scalar(select(User.language).where(User.chat_id.ilike(call.message.chat.id)))
# #                     video = await conn.scalar(
# #                         select(PinterestDB.video_url).where(PinterestDB.video_id.ilike(call.message.text)))
# #                     if video:
# #                         if 'mp4' in video:
# #                             await bot.send_video(chat_id=call.message.chat.id, video=video,
# #                                                  caption=f"{main_caption}{keyboard_saver[language]} 📥")
# #                         else:
# #                             await bot.send_photo(chat_id=call.message.chat.id, photo=video,
# #                                                  caption=f"{main_caption}{keyboard_saver[language]} 📥")
# #                     else:
# #                         waiting_msg = await bot.send_message(chat_id=call.message.chat.id,
# #                                                              text=f"📥 {keyboard_waiting[language]}")
# #                         async with aiohttp.ClientSession() as session:
# #                             video_url = await pinterest_downloader(call.message.text, session=session)
# #                         if 'mp4' in video_url:
# #                             await waiting_msg.delete()
# #                             await bot.send_video(chat_id=call.message.chat.id, video=video_url,
# #                                                  caption=f"{main_caption}{keyboard_saver[language]} 📥")
# #                         else:
# #                             await waiting_msg.delete()
# #                             await bot.send_photo(chat_id=call.message.chat.id, photo=video_url,
# #                                                  caption=f"{main_caption}{keyboard_saver[language]} 📥")
# #                         await pinterest_db(call.message.text, video_url, conn)
# #
# #         if not  await check_subscription():
# #             await check_subscription(message=message)
# #             await check_subscription(call=call)
# #
# #
# #     except Exception as e:
# #         logger.exception("Error while sending Pinterest video: %s", e)
