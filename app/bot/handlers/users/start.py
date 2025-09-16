# app/bot/handlers/start.py
from aiogram import Router, F
from aiogram.enums import ChatType
from aiogram.filters import CommandStart, StateFilter, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.bot.handlers.users.kb import get_add_to_group, get_language_keyboard, cancel
from app.bot.handlers.users.translations import choose_button, terms, privacy, t
from app.bot.utils import LanguageSelection
from app.core.config import bot
from app.core.logger import get_logger
from app.db.services.redis_manager import RedisManager
from app.db.services.user_service import get_lang_cache_then_db, ensure_user_exists

router = Router()


@router.message(CommandStart(), StateFilter('*'), F.chat.type == ChatType.PRIVATE)
async def start_handler(message: Message, state: FSMContext, **data):
    await message.delete()
    await state.clear()
    db = data.get("db")
    rid = data.get("request_id")
    logger = get_logger(rid)
    tg_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    is_premium = getattr(message.from_user, "is_premium", False)
    redis = RedisManager.client()
    lang = await get_lang_cache_then_db(session=db, redis_client=redis, chat_id=tg_id)
    if lang:
        return await bot.send_message(
            chat_id=message.chat.id,
            text=t(lang, "start"),
            reply_markup=get_add_to_group(lang),
            disable_web_page_preview=True,
        )
    try:
        parts = message.text.split()
        added_by = parts[1] if len(parts) > 1 else 'bot'
        user_id = await ensure_user_exists(
            session=db,
            chat_id=tg_id,
            username=username,
            first_name=first_name,
            is_premium=is_premium,
            default_lang=None,
            added_by=added_by
        )
        if getattr(db, "session_created", False):
            db.info["committed_by_handler"] = True
            await db.commit()
        logger.info("start: ensured user id=%s chat_id=%s", user_id, tg_id)
    except Exception:
        logger.exception("start: ensure_user failed")
        try:
            if getattr(db, "session_created", False):
                await db.rollback()
        except Exception:
            logger.exception("start: rollback failed")
        return await message.answer("Server error, try again later.")
    await bot.send_message(chat_id=message.chat.id, text=choose_button, reply_markup=get_language_keyboard())
    return await state.set_state(LanguageSelection.select_language)


@router.message(Command("lang"), StateFilter('*'), F.chat.type == ChatType.PRIVATE)
async def lang_command(message: Message, state: FSMContext, **data):
    await message.delete()
    await state.clear()
    db = data.get("db")
    rid = data.get("request_id")
    logger = get_logger(rid)
    tg_id = message.from_user.id
    redis = RedisManager.client()
    lang = await get_lang_cache_then_db(session=db, redis_client=redis, chat_id=tg_id)
    await bot.send_message(chat_id=message.chat.id, text=choose_button, reply_markup=get_language_keyboard())
    await state.set_state(LanguageSelection.select_language)


@router.message(Command("help"), StateFilter('*'), F.chat.type == ChatType.PRIVATE)
async def lang_command(message: Message, state: FSMContext, **data):
    await message.delete()
    await state.clear()
    db = data.get("db")
    rid = data.get("request_id")
    logger = get_logger(rid)
    tg_id = message.from_user.id
    redis = RedisManager.client()
    lang = await get_lang_cache_then_db(session=db, redis_client=redis, chat_id=tg_id)
    await bot.send_message(chat_id=message.chat.id, text=t(lang,'help'), reply_markup=cancel)


@router.message(Command("terms"), StateFilter('*'))
async def handler_in_specific_state(message: Message, state: FSMContext):
    await message.delete()
    await state.clear()
    return await bot.send_message(chat_id=message.chat.id, text=terms, reply_markup=cancel, protect_content=True)


@router.message(Command("privacy"), StateFilter('*'))
async def handler_in_specific_state(message: Message, state: FSMContext):
    await message.delete()
    await state.clear()
    return await bot.send_message(chat_id=message.chat.id, text=privacy, reply_markup=cancel, protect_content=True)
