import time

from aiogram.dispatcher import FSMContext
from aiogram.types import InputMediaPhoto, InputMediaVideo
from instagram import instagram_api
from db.models import *
from data import *
from keyboards import *

waiting_msg_data = {}


@dp.message_handler(commands=['start'], chat_type=types.ChatType.PRIVATE)
async def start_handler_lang(message: types.Message):
    await message.delete()
    try:
        language = await User.get_language(chat_id=message.chat.id)
        if language:
            await bot.send_message(
                chat_id=message.chat.id,
                text=langs_text.get(language).get('start'),
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
            added_by = 'true' if message.text == '/start' else message.text.split(' ')[-1]
            waiting_msg_data[message.chat.id] = {'added_by': added_by}
            await LanguageSelection.select_language.set()
    except Exception as e:
        logger.exception("Error while processing start command: %s", e)


@dp.callback_query_handler(lambda c: c.data in languages.keys(), state=LanguageSelection.select_language,
                           chat_type=types.ChatType.PRIVATE)
async def process_language_selection(call: types.CallbackQuery, state: FSMContext):
    try:
        if call.message.chat.id in waiting_msg_data:
            user_data = waiting_msg_data.pop(call.message.chat.id)
            added_by = user_data['added_by']
            language = languages.get(call.data)
            await User.create_user(
                chat_id=call.message.chat.id,
                username=call.message.chat.username,
                first_name=call.message.chat.first_name,
                language=language,
                added_by=added_by,
                created_add=datetime.now()
            )
            await state.finish()
            await bot.answer_callback_query(callback_query_id=call.id)
            await bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=langs_text.get(language).get('start'),
                reply_markup=add_group.get(language),
                disable_web_page_preview=True
            )
        return await call.message.delete()
    except Exception as e:
        logger.exception("Error while processing language selection: %s", e)


@dp.message_handler(commands=['lang'], chat_type=types.ChatType.PRIVATE)
async def change_language_handler(message: types.Message):
    try:
        await message.delete()
        await bot.send_message(
            chat_id=message.chat.id,
            text=choose_button,
            reply_markup=language_keyboard,
            protect_content=True
        )
        await LanguageChange.select_language.set()
    except Exception as e:
        await bot.send_message(
            chat_id=message.chat.id,
            text="You haven't selected a language yet. Please use the /start command to select a language.",
            protect_content=True
        )


@dp.callback_query_handler(lambda c: c.data in languages.keys(), state=LanguageChange.select_language,
                           chat_type=types.ChatType.PRIVATE)
async def process_change_language(call: types.CallbackQuery, state: FSMContext):
    try:
        language = languages.get(call.data)
        await User.update_language(chat_id=call.message.chat.id, update_lang=language)
        await state.finish()
        await bot.answer_callback_query(callback_query_id=call.id)
        await bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=langs_text.get(language).get('start'),
            reply_markup=add_group.get(language),
            disable_web_page_preview=True
        )
    except Exception as e:
        logger.exception("Error while changing language preference: %s", e)


@dp.message_handler(commands=['help'])
async def help_handler(message: types.Message):
    try:
        await message.delete()
        if message.chat.type != types.ChatType.PRIVATE:
            language = await Group.get_language(chat_id=message.chat.id)
            await bot.send_message(
                chat_id=message.chat.id,
                reply_markup=del_help,
                text=f"<b>{langs_text.get(language).get('help')}</b>",
                disable_web_page_preview=True,
                protect_content=True
            )
        else:
            language = await User.get_language(chat_id=message.chat.id)
            await bot.send_message(
                chat_id=message.chat.id,
                text=f"<b>{langs_text.get(language).get('help')}</b>",
                reply_markup=del_help,
                disable_web_page_preview=True,
                protect_content=True
            )
    except Exception as e:
        logger.exception("Error while processing start command: %s", e)


@dp.message_handler(regexp=r'https?:\/\/(www\.)?instagram\.com\/(reel|p)\/([-_a-zA-Z0-9]{11})',
                    chat_type=types.ChatType.PRIVATE)
async def send_instagram_media(message: types.Message):
    await message.delete()
    global wait_msg
    language = await User.get_language(chat_id=message.chat.id)
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


@dp.message_handler(regexp=r'https?:\/\/(www\.)?instagram\.com\/(stories)', chat_type=types.ChatType.PRIVATE)
async def send_instagram_media(message: types.Message):
    await message.delete()
    global wait_msg
    language = await User.get_language(chat_id=message.chat.id)
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
