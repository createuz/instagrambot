import time

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import Message
from keyboards import choose_button, language_keyboard, langs_text, add_group, languages

from api import PINTEREST_URL_REGEX
from data import dp, bot, logger
from data import main_caption
from db import Group
from handlers1 import pinterest_api


@dp.message_handler(commands=['start'])
async def start_handler_lang(message: types.Message):
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
            await Group.update_language(chat_id=call.message.chat.id, language=language)
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
            members = await bot.get_chat_members_count(chat_id=call.message.chat.id)
            await Group.create_group(
                chat_id=call.message.chat.id,
                name=call.message.chat.title,
                username=call.message.chat.username,
                members=members,
                language=language,
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


@dp.message_handler(regexp=PINTEREST_URL_REGEX)
async def send_pinterest_all_media(message: Message):
    global wait_msg
    link = message.text
    await message.delete()
    language = await Group.get_language(message.chat.id)
    try:
        cached_data = pinterest_api.cache.get(link, {})
        if cached_data.get('timestamp', 0) >= time.time() - 2629746:
            media = cached_data.get('result')
            if 'mp4' in media:
                return await bot.send_video(
                    chat_id=message.chat.id,
                    video=media,
                    caption=f"<b>{main_caption} {langs_text.get(language).get('saved')} 📥</b>"
                )
            if 'jpg' in media:
                return await bot.send_photo(
                    chat_id=message.chat.id,
                    photo=media,
                    caption=f"<b>{main_caption} {langs_text.get(language).get('saved')} 📥</b>"
                )
        wait_msg = await bot.send_message(
            chat_id=message.chat.id,
            text=f"<b>{langs_text.get(language).get('waiting')}</b>",
            protect_content=True
        )
        urls = await pinterest_api.pinterest_downloader(link=link)
        if urls is None or not urls:
            await wait_msg.delete()
            return await bot.send_message(
                chat_id=message.chat.id,
                text=langs_text.get(language).get('error').format(message.text),
                disable_web_page_preview=True
            )
        if 'mp4' in urls:
            await bot.send_video(
                chat_id=message.chat.id,
                video=urls,
                caption=f"<b>{main_caption} {langs_text.get(language).get('saved')} 📥</b>"
            )
        if 'jpg' in urls:
            await bot.send_photo(
                chat_id=message.chat.id,
                photo=urls,
                caption=f"<b>{main_caption} {langs_text.get(language).get('saved')} 📥</b>"
            )
        await wait_msg.delete()
        pinterest_api.cache[link] = {'result': urls, 'timestamp': time.time()}
    except Exception as e:
        logger.exception("Error while sending Instagram photo: %s", e)
        return await bot.send_message(
            chat_id=message.chat.id,
            text=langs_text.get(language).get('error').format(message.text),
            disable_web_page_preview=True
        )


@dp.message_handler(commands=['help'])
async def help_handler(message: Message):
    try:
        if message.chat.type != ChatType.PRIVATE:
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
    await message.delete()
