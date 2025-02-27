from aiogram import Router, F
from aiogram.enums import ChatType
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from data import LanguageSelection, bot, LanguageChange, logger
from db import User, db
from .kb import get_language_keyboard, get_add_to_group, cancel
from .langs import choose_button, langs_text, languages, language_changed, terms, privacy

user_router = Router()


@user_router.message(CommandStart(), F.chat.type == ChatType.PRIVATE, StateFilter('*'))
async def start_handler(message: Message, state: FSMContext):
    await message.delete()
    await state.clear()
    try:
        language = await User.get_language(message.chat.id)
        if not language:
            await bot.send_message(
                chat_id=message.chat.id,
                text=choose_button,
                reply_markup=get_language_keyboard(),
            )
            parts = message.text.split()
            added_by = parts[1] if len(parts) > 1 else 'true'
            await state.update_data(added_by=added_by)
            await state.set_state(LanguageSelection.select_language)
        else:
            await bot.send_message(
                chat_id=message.chat.id,
                text=langs_text[language]['start'],
                reply_markup=get_add_to_group()[language],
                disable_web_page_preview=True,
            )
    except Exception as e:
        logger.exception("Error in start_handler: %s", e)


@user_router.callback_query(F.data.in_(languages.keys()), LanguageSelection.select_language)
async def create_user_handler(call: CallbackQuery, state: FSMContext):
    try:
        language = languages[call.data]
        data = await state.get_data()
        is_premium: bool = True if call.message.from_user.is_premium else False
        async with db.get_session() as session:
            new_user = await User.create_user(
                session=session,
                chat_id=call.message.chat.id,
                username=call.message.chat.username,
                first_name=call.message.chat.first_name,
                is_premium=is_premium,
                language=language,
                added_by=data.get('added_by')
            )
            await session.refresh(new_user)
        await bot.answer_callback_query(call.id, f"✅ {language_changed[call.data]}")
        await bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=langs_text[language]['start'],
            reply_markup=get_add_to_group()[language],
            disable_web_page_preview=True
        )
        await state.clear()
    except Exception as e:
        logger.exception("Error in create_user_handler: %s", e)


@user_router.message(Command("lang"), F.chat.type == ChatType.PRIVATE, StateFilter('*'))
async def change_language_handler(message: Message, state: FSMContext):
    await message.delete()
    await state.clear()
    try:
        await bot.send_message(
            chat_id=message.chat.id,
            text=choose_button,
            reply_markup=get_language_keyboard(),
        )
        await state.set_state(LanguageChange.select_language)
    except Exception as e:
        logger.exception("Error in change_language_handler: %s", e)
        await bot.send_message(chat_id=message.chat.id, text="Please use the /start command to select a language.")


@user_router.callback_query(F.data.in_(languages.keys()), LanguageChange.select_language)
async def process_change_language(call: CallbackQuery, state: FSMContext):
    try:
        chat_id = call.message.chat.id
        language = languages[call.data]
        await bot.answer_callback_query(call.id, f"✅ {language_changed[call.data]}")
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=call.message.message_id,
            text=langs_text[language]['start'],
            reply_markup=get_add_to_group()[language],
            disable_web_page_preview=True
        )
        await User.update_language(chat_id, language)
        await state.clear()
    except Exception as e:
        logger.exception("Error in process_change_language: %s", e)


@user_router.message(Command("help"), StateFilter('*'))
async def handler_in_specific_state(message: Message, state: FSMContext):
    await message.delete()
    language = await User.get_language(message.chat.id)
    await bot.send_message(
        chat_id=message.chat.id,
        text=langs_text[language]['help'],
        reply_markup=cancel,
    )
    await state.clear()


@user_router.message(Command("terms"), StateFilter('*'))
async def handler_in_specific_state(message: Message, state: FSMContext):
    await message.delete()
    await bot.send_message(chat_id=message.chat.id, text=terms, reply_markup=cancel, protect_content=True)
    await state.clear()


@user_router.message(Command("privacy"), StateFilter('*'))
async def handler_in_specific_state(message: Message, state: FSMContext):
    await message.delete()
    await bot.send_message(chat_id=message.chat.id, text=privacy, reply_markup=cancel, protect_content=True)
    await state.clear()
