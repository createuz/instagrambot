import re
import time
from aiogram.dispatcher import FSMContext
from aiogram.types import InputMediaPhoto, InputMediaVideo
import keyboards
from data import *
from aiogram import types
from handlers import instagram_api
from keyboards import *
from utlis.models import *


@dp.message_handler(commands=['start'])
async def save_group_info(message: types.Message):
    try:
        group_lang = await Group.get_language(message.chat.id)
        if group_lang:
            await bot.send_message(message.chat.id, text=f"<b>{select_dict[group_lang]}</b>",
                                   reply_markup=keyboard_group[group_lang],
                                   disable_web_page_preview=True, protect_content=True)
        else:
            await bot.send_message(message.chat.id, text=choose_button, reply_markup=language_keyboard,
                                   protect_content=True)
    except Exception as e:
        logger.exception("Error while processing start command: %s", e)


@dp.message_handler(commands=['lang'])
async def change_language_handler_group(message: types.Message):
    chat_id = message.chat.id
    try:
        await bot.send_message(chat_id, text=choose_button, reply_markup=language_keyboard, protect_content=True)
    except Exception as e:
        logger.exception("Error while processing language selection: %s", e)


@dp.callback_query_handler(lambda c: c.data in languages.keys())
async def process_language_selection(call: types.CallbackQuery, state: FSMContext):
    selected_language = call.data
    chat_id = call.message.chat.id
    group_username = call.message.chat.username
    language = languages[selected_language]
    group_name = call.message.chat.title
    try:
        group_lang = await Group.get_language(chat_id)
        if group_lang:
            await Group.update_language(chat_id, language)
            await state.finish()
            await bot.answer_callback_query(call.id)
            callback_id = call.message.message_id
            await bot.edit_message_text(chat_id=chat_id, message_id=callback_id, text=f"<b>{select_dict[language]}</b>",
                                        reply_markup=keyboard_group[language], disable_web_page_preview=True)
        else:
            chat_members = await bot.get_chat_members_count(chat_id)
            await Group.create_group(chat_id, group_name, group_username, chat_members, language)

            await state.finish()
            await bot.answer_callback_query(call.id)
            callback_id = call.message.message_id
            await bot.edit_message_text(chat_id=chat_id, message_id=callback_id, text=f"<b>{select_dict[language]}</b>",
                                        reply_markup=keyboard_group[language], disable_web_page_preview=True)
    except Exception as e:
        logger.exception("Error while processing language selection: %s", e)


@dp.message_handler(regexp=r'https?:\/\/(www\.)?instagram\.com\/(reel|p)\/([-_a-zA-Z0-9]{11})')
async def send_instagram_media(message: types.Message):
    global waiting_msg, delete_msg
    link = message.text
    language = await Group.get_language(message.chat.id)
    await message.delete()
    match = re.search(r'https://www.instagram.com/(?:p|reel)/([-_a-zA-Z0-9]{11})', link)
    vid = match.group(1) if match else None
    try:
        cached_data = instagram_api.cache.get(vid, {})
        if cached_data.get('timestamp', 0) >= time.time() - 2629746:
            media = cached_data.get('result')
            return await bot.send_media_group(chat_id=message.chat.id, media=media)
        waiting_msg = await bot.send_message(chat_id=message.chat.id,
                                             text=f"<b>📥 {keyboards.keyboard_waiting[language]}</b>",
                                             protect_content=True)
        urls = await instagram_api.instagram_downloader(vid=vid)
        if urls is None or not urls:
            await waiting_msg.delete()
            return await bot.send_message(message.chat.id, text=keyboards.down_err[language].format(link),
                                          disable_web_page_preview=True, protect_content=True)
        media = [InputMediaPhoto(url) if 'jpg' in url else InputMediaVideo(url) for url in urls]
        media[-1].caption = f"<b>📥 {main_caption}{keyboards.keyboard_saver[language]}</b>"
        await bot.send_media_group(chat_id=message.chat.id, media=media)
        await waiting_msg.delete()
        instagram_api.cache[vid] = {'result': media, 'timestamp': time.time()}
    except Exception as e:
        await waiting_msg.delete()
        logger.exception("Error while sending Instagram photo: %s", e)
        return await bot.send_message(message.chat.id, text=keyboards.down_err[language].format(link),
                                      disable_web_page_preview=True, protect_content=True)


@dp.message_handler(regexp=r'https?:\/\/(www\.)?instagram\.com\/(stories)')
async def send_instagram_media(message: types.Message):
    link = message.text
    await message.delete()
    language = await Group.get_language(message.chat.id)
    waiting_msg = await bot.send_message(chat_id=message.chat.id,
                                         text=f"<b>📥 {keyboards.keyboard_waiting[language]}</b>", protect_content=True)
    try:
        urls = await instagram_api.instagram_stories(link=link)
        if urls is None or not urls:
            await waiting_msg.delete()
            return await bot.send_message(message.chat.id, text=keyboards.down_err[language].format(link),
                                          disable_web_page_preview=True, protect_content=True)
        media_groups = [urls[i:i + 10] for i in range(0, len(urls), 10)]
        for group in media_groups:
            media = [InputMediaPhoto(url) if 'jpg' in url else InputMediaVideo(url) for url in group]
            media[-1].caption = f"📥 <b>{main_caption}{keyboards.keyboard_saver[language]}</b>"
            await bot.send_media_group(chat_id=message.chat.id, media=media)
        await waiting_msg.delete()
    except Exception as e:
        logger.exception("Error while sending Instagram photo: %s", )
        await waiting_msg.delete()
        return await bot.send_message(message.chat.id, text=keyboards.down_err[language].format(link),
                                      disable_web_page_preview=True, protect_content=True)
