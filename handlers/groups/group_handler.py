import time
from aiogram.dispatcher import FSMContext
from aiogram.types import InputMediaPhoto, InputMediaVideo
from data import *
from aiogram import types
from handlers import instagram_api
from keyboards import *
from db.models import *


@dp.message_handler(commands=['start'])
async def start_handler_lang(message: types.Message):
    await message.delete()
    try:
        language = await Group.get_language(message.chat.id)
        if language:
            await bot.send_message(
                chat_id=message.chat.id,
                text=f"<b>{langs_text.get(language).get('start')}</b>",
                reply_markup=add_group.get(language),
                disable_web_page_preview=True,
                protect_content=True
            )
        else:
            await bot.send_message(
                chat_id=message.chat.id,
                text=choose_button,
                reply_markup=language_keyboard,
                protect_content=True
            )
            await LanguageSelection.select_language.set()
    except Exception as e:
        logger.exception("Error while processing start command: %s", e)


@dp.message_handler(commands=['lang'])
async def change_language_handler_group(message: types.Message):
    try:
        await bot.send_message(
            chat_id=message.chat.id,
            text=choose_button,
            reply_markup=language_keyboard,
            protect_content=True
        )
    except Exception as e:
        await bot.send_message(
            chat_id=message.chat.id,
            text="You haven't selected a language yet. Please use the /start command to select a language.",
            protect_content=True
        )


@dp.callback_query_handler(lambda c: c.data in languages.keys())
async def process_language_selection(call: types.CallbackQuery, state: FSMContext):
    try:
        language = languages.get(call.data)
        group_lang = await Group.get_language(chat_id=call.message.chat.id)
        if group_lang:
            await Group.update_language(chat_id=call.message.chat.id, new_language=language)
            await state.finish()
            await bot.answer_callback_query(callback_query_id=call.id)
            await bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=f"<b>{langs_text.get(language).get('start')}</b>",
                reply_markup=add_group.get(language),
                disable_web_page_preview=True
            )
        else:
            chat_members = await bot.get_chat_members_count(chat_id=call.message.chat.id)
            await Group.create_group(
                chat_id=call.message.chat.id,
                group_name=call.message.chat.title,
                group_username=call.message.chat.username,
                group_members=chat_members,
                language=language
            )
            await bot.answer_callback_query(callback_query_id=call.id)
            await state.finish()
            await bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=f"<b>{langs_text.get(language).get('start')}</b>",
                reply_markup=add_group.get(language),
                disable_web_page_preview=True
            )
    except Exception as e:
        logger.exception("Error while processing language selection: %s", e)


@dp.message_handler(regexp=r'https?:\/\/(www\.)?instagram\.com\/(reel|p)\/([-_a-zA-Z0-9]{11})')
async def send_instagram_media(message: types.Message):
    await message.delete()
    global wait_msg
    language = await Group.get_language(chat_id=message.chat.id)
    try:
        cached_data = instagram_api.cache.get(message.text, {})
        if cached_data.get('timestamp', 0) >= time.time() - 2629746:
            media = cached_data.get('result')
            return await bot.send_media_group(chat_id=message.chat.id, media=media)
        wait_msg = await bot.send_message(
            chat_id=message.chat.id,
            text=f"<b>{langs_text.get(language).get('waiting')}</b>",
            protect_content=True
        )
        urls = await instagram_api.instagram_downloader(link=message.text)
        if urls is None or not urls:
            await wait_msg.delete()
            return await bot.send_message(
                chat_id=message.chat.id,
                text=langs_text.get(language).get('error').format(message.text),
                disable_web_page_preview=True
            )
        media = [InputMediaPhoto(url) if 'jpg' in url else InputMediaVideo(url) for url in urls]
        media[-1].caption = f"<b>{main_caption}{langs_text.get(language).get('saved')} 📥</b>"
        await bot.send_media_group(chat_id=message.chat.id, media=media)
        await wait_msg.delete()
        instagram_api.cache[message.text] = {'result': media, 'timestamp': time.time()}
    except Exception as e:
        await wait_msg.delete()
        logger.exception("Error while sending Instagram photo: %s", e)
        return await bot.send_message(
            chat_id=message.chat.id,
            text=langs_text.get(language).get('error').format(message.text),
            disable_web_page_preview=True
        )


@dp.message_handler(regexp=r'https?:\/\/(www\.)?instagram\.com\/(stories)')
async def send_instagram_media(message: types.Message):
    await message.delete()
    global wait_msg
    language = await Group.get_language(chat_id=message.chat.id)
    try:
        wait_msg = await bot.send_message(
            chat_id=message.chat.id,
            text=f"<b>{langs_text.get(language).get('waiting')}</b>",
            protect_content=True
        )
        urls = await instagram_api.instagram_downloader(link=message.text)
        if urls is None or not urls:
            await wait_msg.delete()
            return await bot.send_message(
                chat_id=message.chat.id,
                text=langs_text.get(language).get('error').format(message.text),
                disable_web_page_preview=True
            )
        media_groups = [urls[i:i + 10] for i in range(0, len(urls), 10)]
        for group in media_groups:
            media = [InputMediaPhoto(url) if 'jpg' in url else InputMediaVideo(url) for url in group]
            media[-1].caption = f"<b>{main_caption}{langs_text.get(language).get('saved')} 📥</b>"
            await bot.send_media_group(chat_id=message.chat.id, media=media)
        await wait_msg.delete()
    except Exception as e:
        logger.exception("Error while sending Instagram photo: %s", )
        await wait_msg.delete()
        return await bot.send_message(
            chat_id=message.chat.id,
            text=langs_text.get(language).get('error').format(message.text),
            disable_web_page_preview=True
        )
