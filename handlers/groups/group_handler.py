from keyboards import *
from downloader import *
from databasedb.models import *
from loader import *


@dp.message_handler(commands=['start'], chat_type=types.ChatType.SUPERGROUP or types.ChatType.GROUP)
async def save_group_info(message: types.Message):
    try:
        language = await Group.get_language(message.chat.id)
        if language:
            await bot.send_message(message.chat.id, text=f"<b>{select_dict[language]}</b>",
                                   reply_markup=keyboard_group[language],
                                   disable_web_page_preview=True)
        else:
            await bot.send_message(message.chat.id, text=choose_button, reply_markup=language_keyboard)
    except Exception as e:
        logger.exception("Error while processing start command: %s", e)


@dp.message_handler(commands=['lang'], chat_type=types.ChatType.SUPERGROUP or types.ChatType.GROUP)
async def change_language_handler_group(message: types.Message):
    chat_id = message.chat.id
    try:
        await bot.send_message(chat_id, text=choose_button, reply_markup=language_keyboard)
    except Exception as e:
        logger.exception("Error while processing language selection: %s", e)


@dp.callback_query_handler(lambda c: c.data in languages.keys(),
                           chat_type=types.ChatType.SUPERGROUP or types.ChatType.GROUP)
async def process_language_selection(callback_query: types.CallbackQuery, state: FSMContext):
    selected_language = callback_query.data
    chat_id = callback_query.message.chat.id
    group_username = callback_query.message.chat.username
    language = languages[selected_language]
    group_name = callback_query.message.chat.title
    try:
        group_lang = await Group.get_language(chat_id)

        if group_lang:
            await Group.update_language(chat_id, language)
            await state.finish()
            await bot.answer_callback_query(callback_query.id)
            callback_id = callback_query.message.message_id
            await bot.edit_message_text(chat_id=chat_id, message_id=callback_id, text=f"<b>{select_dict[language]}</b>",
                                        reply_markup=keyboard_group[language], disable_web_page_preview=True)
        else:
            chat_members = await bot.get_chat_members_count(chat_id)
            await Group.create_group(chat_id, group_name, group_username, chat_members, language)
            await state.finish()
            await bot.answer_callback_query(callback_query.id)
            callback_id = callback_query.message.message_id
            await bot.edit_message_text(chat_id=chat_id, message_id=callback_id, text=f"<b>{select_dict[language]}</b>",
                                        reply_markup=keyboard_group[language], disable_web_page_preview=True)
    except Exception as e:
        logger.exception("Error while processing language selection: %s", e)


@dp.message_handler(regexp=r'https?:\/\/(www\.)?instagram\.com\/(reel|p|tv)\/([-_a-zA-Z0-9]{11})',
                    chat_type=types.ChatType.SUPERGROUP or types.ChatType.GROUP)
async def send_instagram_media(message: types.Message):
    link = message.text
    await message.delete()
    try:
        language = await Group.get_language(message.chat.id)
        insta_data = await InstagramMediaDB.get_video_url(message.text)
        if insta_data:
            media = [InputMediaPhoto(url) if 'jpg' in url else InputMediaVideo(url) for url in
                     insta_data]
            media[-1].caption = f"<b>📥 {main_caption}{keyboard_saver[language]}</b>"
            await bot.send_media_group(chat_id=message.chat.id, media=media)
        else:
            waiting_msg = await bot.send_message(chat_id=message.chat.id,
                                                 text=f"<b>📥 {keyboard_waiting[language]}</b>")
            async with aiohttp.ClientSession() as session:
                urls = await instagram_downloader_photo_video(link, session=session)
                await waiting_msg.delete()
                media = [InputMediaPhoto(url) if 'jpg' in url else InputMediaVideo(url) for url in
                         urls]
                media[-1].caption = f"<b>📥 {main_caption}{keyboard_saver[language]}</b>"
                await bot.send_media_group(chat_id=message.chat.id, media=media)
            await InstagramMediaDB.create_media_list(message.text, urls)
    except Exception as e:
        await bot.delete_message(message.chat.id, message_id=message.message_id)
        logger.exception("Error while sending Instagram photo: %s", e)


@dp.message_handler(regexp=r'https?:\/\/(www\.)?instagram\.com\/(stories)',
                    chat_type=types.ChatType.SUPERGROUP or types.ChatType.GROUP)
async def send_instagram_media(message: types.Message):
    link = message.text
    await message.delete()
    try:
        language = await Group.get_language(message.chat.id)
        waiting_msg = await bot.send_message(chat_id=message.chat.id,
                                             text=f"<b>📥 {keyboard_waiting[language]}</b>")
        async with aiohttp.ClientSession() as session:
            urls = await instagram_downloader_photo_video(link, session=session)
            await waiting_msg.delete()
            media_groups = [urls[i:i + 10] for i in range(0, len(urls), 10)]
            for group in media_groups:
                media = [InputMediaPhoto(url) if 'jpg' in url else InputMediaVideo(url) for url in group]
                media[-1].caption = f"<b>📥 {main_caption}{keyboard_saver[language]}</b>"
                await bot.send_media_group(chat_id=message.chat.id, media=media)
    except Exception as e:
        await bot.delete_message(message.chat.id, message_id=message.message_id)
        logger.exception("Error while sending Instagram photo: %s", e)
