from aiogram.dispatcher import FSMContext
from aiogram.types import InputMediaPhoto, InputMediaVideo

import keyboards
from download import *
from data import *
from utlis.models import *
from aiogram import types


@dp.message_handler(commands=['start'], chat_type=types.ChatType.PRIVATE)
async def start_handler_lang(message: types.Message):
    await bot.send_video(message.chat.id,
                         'https://instagram.ftas10-1.fna.fbcdn.net/o1/v/t16/f1/m69/GCnH7ROVfsQ-gwADANrlKzQdqq1SbpR1AAAF.mp4?efg=eyJxZV9ncm91cHMiOiJbXCJpZ193ZWJfZGVsaXZlcnlfdnRzX290ZlwiXSIsInZlbmNvZGVfdGFnIjoidnRzX3ZvZF91cmxnZW4uY2xpcHMuYzIuMTA4MC5oaWdoIn0&_nc_ht=instagram.ftas10-1.fna.fbcdn.net&_nc_cat=110&vs=249754724780452_488212320&_nc_vs=HBksFQIYOnBhc3N0aHJvdWdoX2V2ZXJzdG9yZS9HQ25IN1JPVmZzUS1nd0FEQU5ybEt6UWRxcTFTYnBSMUFBQUYVAALIAQAVAhg6cGFzc3Rocm91Z2hfZXZlcnN0b3JlL0dLVzNTQWVtRDVSOWZENERBTVZ3QnB1ZnVVWWxicFIxQUFBRhUCAsgBACgAGAAbABUAACaUlM%2FP4r7MPxUCKAJDMywXQCQAAAAAAAAYEmRhc2hfaGlnaF8xMDgwcF92MREAdf4HAA%3D%3D&_nc_rid=f5503844b5&ccb=9-4&oh=00_AfBA11UNmyNnxHvBvJ-gmrJ3ABZkHHe9cNoWRKE4I80zlg&oe=6567939A&_nc_sid=4f4799')
    # await message.delete()
    # try:
    #     language = await User.get_language(message.chat.id)
    #     if language:
    #         await bot.send_message(message.from_id, text=f"<b>{keyboards.select_dict[language]}</b>",
    #                                reply_markup=keyboards.keyboard_group[language],
    #                                disable_web_page_preview=True, protect_content=True)
    #     else:
    #         await bot.send_message(message.chat.id, text=keyboards.choose_button,
    #                                reply_markup=keyboards.language_keyboard,
    #                                protect_content=True)
    #         await LanguageSelection.select_language.set()
    # except Exception as e:
    #     logger.exception("Error while processing start command: %s", e)


@dp.callback_query_handler(lambda c: c.data in keyboards.languages.keys(), state=LanguageSelection.select_language,
                           chat_type=types.ChatType.PRIVATE)
async def process_language_selection(callback_query: types.CallbackQuery, state: FSMContext):
    selected_language = callback_query.data
    chat_id = callback_query.message.chat.id
    username = callback_query.message.chat.username
    first_name = callback_query.from_user.first_name
    language = keyboards.languages[selected_language]
    created_add = datetime.now()
    try:
        await User.create_user(chat_id, username, first_name, language, created_add)
        await state.finish()
        await bot.answer_callback_query(callback_query.id)
        callback_id = callback_query.message.message_id
        await bot.edit_message_text(chat_id=chat_id, message_id=callback_id,
                                    text=f"<b>{keyboards.select_dict[language]}</b>",
                                    reply_markup=keyboards.keyboard_group[language], disable_web_page_preview=True)
    except Exception as e:
        logger.exception("Error while processing language selection: %s", e)


@dp.message_handler(commands=['lang'], chat_type=types.ChatType.PRIVATE)
async def change_language_handler(message: types.Message):
    chat_id = message.chat.id
    await message.delete()
    try:
        await bot.send_message(chat_id, text=keyboards.choose_button, reply_markup=keyboards.language_keyboard,
                               protect_content=True)
        await LanguageChange.select_language.set()
    except Exception as e:
        await bot.send_message(message.chat.id,
                               "You haven't selected a language yet. Please use the /start command to select a language.",
                               protect_content=True)


@dp.callback_query_handler(lambda c: c.data in keyboards.languages.keys(), state=LanguageChange.select_language,
                           chat_type=types.ChatType.PRIVATE)
async def process_change_language(callback_query: types.CallbackQuery, state: FSMContext):
    selected_language = callback_query.data
    chat_id = callback_query.message.chat.id
    language = keyboards.languages[selected_language]
    try:
        await User.update_language(chat_id, language)
        await state.finish()
        await bot.answer_callback_query(callback_query.id)
        callback_id = callback_query.message.message_id
        await bot.edit_message_text(chat_id=chat_id, message_id=callback_id,
                                    text=f"<b>{keyboards.select_dict[language]}</b>",
                                    reply_markup=keyboards.keyboard_group[language], disable_web_page_preview=True)
    except Exception as e:
        logger.exception("Error while changing language preference: %s", e)


@dp.message_handler(commands=['help'])
async def help_handler(message: types.Message):
    await message.delete()
    try:
        if message.chat.type != types.ChatType.PRIVATE:
            language = await Group.get_language(message.chat.id)
            await bot.send_message(message.chat.id, text=keyboards.help_dict[language], disable_web_page_preview=True,
                                   protect_content=True)
        else:
            language = await User.get_language(message.chat.id)
            await bot.send_message(message.chat.id, text=f"<b>{keyboards.help_dict[language]}</b>",
                                   disable_web_page_preview=True, protect_content=True)
    except Exception as e:
        logger.exception("Error while processing start command: %s", e)


@dp.message_handler(regexp=r'https?:\/\/(www\.)?instagram\.com\/(reel|p|tv)\/([-_a-zA-Z0-9]{11})',
                    chat_type=types.ChatType.PRIVATE)
async def send_instagram_media(message: types.Message):
    global waiting_msg, delete_msg
    link = message.text
    language = await User.get_language(message.chat.id)
    try:
        await message.delete()
        waiting_msg = await bot.send_message(chat_id=message.chat.id,
                                             text=f"<b>📥 {keyboards.keyboard_waiting[language]}</b>",
                                             protect_content=True)
        urls = await download_media(link=link)
        if urls is None or not urls:
            await waiting_msg.delete()
            return await bot.send_message(message.chat.id, text=keyboards.down_err[language].format(link),
                                          disable_web_page_preview=True, protect_content=True)
        media = [InputMediaPhoto(url) if 'jpg' in url else InputMediaVideo(url) for url in urls]
        media[-1].caption = f"<b>📥 {main_caption}{keyboards.keyboard_saver[language]}</b>"
        await bot.send_media_group(chat_id=message.chat.id, media=media)
        await waiting_msg.delete()

    except Exception as e:
        await waiting_msg.delete()
        logger.exception("Error while sending Instagram photo: %s", e)
        return await bot.send_message(message.chat.id, text=keyboards.down_err[language].format(link),
                                      disable_web_page_preview=True, protect_content=True)


@dp.message_handler(regexp=r'https?:\/\/(www\.)?instagram\.com\/(stories)', chat_type=types.ChatType.PRIVATE)
async def send_instagram_media(message: types.Message):
    link = message.text
    await message.delete()
    language = await User.get_language(message.chat.id)
    waiting_msg = await bot.send_message(chat_id=message.chat.id,
                                         text=f"<b>📥 {keyboards.keyboard_waiting[language]}</b>", protect_content=True)
    try:
        urls = await download_media(link=link)
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
