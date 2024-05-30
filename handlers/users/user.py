from aiogram.dispatcher import FSMContext
from db.models import *
from data import *
from keyboards import *


@dp.message_handler(commands=['start'], chat_type=types.ChatType.PRIVATE)
async def start_handler(message: types.Message, state: FSMContext):
    await message.delete()
    parts = message.text.split()
    identifier = parts[1] if len(parts) > 1 else None
    try:
        language = await User.get_language(chat_id=message.chat.id)
        if not language:
            await bot.send_message(
                chat_id=message.chat.id,
                text=choose_button,
                reply_markup=language_keyboard,
                protect_content=True
            )
            await state.update_data(added_by=identifier or 'true')
            return await LanguageSelection.select_language.set()
        else:
            await bot.send_message(
                chat_id=message.chat.id,
                text=langs_text.get(language).get('start'),
                reply_markup=add_group.get(language),
                disable_web_page_preview=True,
                protect_content=True
            )
    except Exception as e:
        logger.exception("Error while processing start command: %s", e)


@dp.callback_query_handler(lambda c: c.data in languages, state=LanguageSelection.select_language,
                           chat_type=types.ChatType.PRIVATE)
async def create_user_handler(call: types.CallbackQuery, state: FSMContext):
    chat_id = call.message.chat.id
    language = languages.get(call.data)
    try:
        data = await state.get_data()
        await User.create_user(
            chat_id=chat_id,
            username=call.message.chat.username,
            first_name=call.message.chat.first_name,
            language=language,
            added_by=data.get('added_by')
        )
        await state.finish()
        await bot.answer_callback_query(callback_query_id=call.id, text=f"✅ {language_changed.get(call.data)}")
        await bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=langs_text.get(language).get('start'),
            reply_markup=add_group.get(language),
            disable_web_page_preview=True
        )
    except Exception as e:
        logger.exception("Error while processing language selection: %s", e)


@dp.message_handler(commands=['lang'], chat_type=types.ChatType.PRIVATE)
async def change_language_handler(message: types.Message):
    await message.delete()
    try:
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
        await User.update_language(chat_id=call.message.chat.id, language=language)
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
    await message.delete()
