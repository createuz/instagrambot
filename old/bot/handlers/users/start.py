# old/bot/handlers/start.py
from aiogram import Router, F
from aiogram.enums import ChatType
from aiogram.filters import CommandStart, StateFilter, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from old.bot.handlers.users.keyboards import (
    get_add_to_group,
    get_language_keyboard,
    cancel,
)
from old.bot.handlers.users.translations import (
    choose_button,
    terms,
    privacy,
    t,
    language_changed,
)
from old.bot.utils import LanguageSelection
from old.core.config import bot
from old.core.logger import get_logger
from old.db.services.redis_manager import RedisManager
from old.db.services.user_service import (
    get_lang_cache_then_db,
    ensure_user_exists,
    upsert_user_language,
    redis_set_lang,
)

router = Router()


@router.message(CommandStart(), StateFilter("*"), F.chat.type == ChatType.PRIVATE)
async def start_handler(message: Message, state: FSMContext, **data):
    await message.delete()
    await state.clear()
    db = data.get("db")
    logger = get_logger()
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
        added_by = parts[1] if len(parts) > 1 else "bot"
        user_id = await ensure_user_exists(
            session=db,
            chat_id=tg_id,
            username=username,
            first_name=first_name,
            is_premium=is_premium,
            default_lang=None,
            added_by=added_by,
        )
        if getattr(db, "session_created", False):
            db.info["committed_by_handler"] = True
            await db.commit()
        # logger.info("start: ensured user id=%s chat_id=%s", user_id, tg_id)
    except Exception:
        logger.exception("start: ensure_user failed")
        try:
            if getattr(db, "session_created", False):
                await db.rollback()
        except Exception:
            logger.exception("start: rollback failed")
        return await message.answer("Try again later.")
    await bot.send_message(
        chat_id=message.chat.id,
        text=choose_button,
        reply_markup=get_language_keyboard(),
    )
    return await state.set_state(LanguageSelection.select_language)


@router.callback_query(F.data.startswith("lang:"), LanguageSelection.select_language)
async def lang_callback(call: CallbackQuery, state: FSMContext, **data):
    db = data.get("db")
    logger = get_logger()
    redis = RedisManager.client()
    lang = call.data.split(":", 1)[1].strip()
    tg_id = call.from_user.id
    try:
        user_id = await upsert_user_language(
            session=db, redis_client=redis, chat_id=tg_id, language=lang
        )
        if getattr(db, "session_created", False):
            db.info["committed_by_handler"] = True
            await db.commit()
        # logger.info("lang_callback: upserted id=%s chat_id=%s lang=%s", user_id, tg_id, lang)
    except Exception:
        try:
            if getattr(db, "session_created", False):
                await db.rollback()
        except Exception:
            logger.exception("rollback failed")
        await call.answer("Try again later.", show_alert=True)
        return await state.clear()
    try:
        if redis:
            await redis_set_lang(redis, tg_id, lang)
    except Exception:
        logger.warning("redis set failed for %s", tg_id)

    await call.answer(f"✅ {language_changed.get(lang)}")
    try:
        await call.message.edit_text(
            text=t(lang, "start"),
            reply_markup=get_add_to_group(lang),
            disable_web_page_preview=True,
        )
    except Exception:
        logger.warning("edit message failed")
    return await state.clear()


@router.message(Command("lang"), StateFilter("*"), F.chat.type == ChatType.PRIVATE)
async def lang_command(message: Message, state: FSMContext, **data):
    await message.delete()
    await state.clear()
    db = data.get("db")
    logger = get_logger()
    tg_id = message.from_user.id
    redis = RedisManager.client()
    lang = await get_lang_cache_then_db(session=db, redis_client=redis, chat_id=tg_id)
    await bot.send_message(
        chat_id=message.chat.id,
        text=choose_button,
        reply_markup=get_language_keyboard(),
    )
    await state.set_state(LanguageSelection.select_language)


@router.message(Command("help"), StateFilter("*"), F.chat.type == ChatType.PRIVATE)
async def lang_command(message: Message, state: FSMContext, **data):
    await message.delete()
    await state.clear()
    db = data.get("db")
    logger = get_logger()
    tg_id = message.from_user.id
    redis = RedisManager.client()
    lang = await get_lang_cache_then_db(session=db, redis_client=redis, chat_id=tg_id)
    await bot.send_message(
        chat_id=message.chat.id, text=t(lang, "help"), reply_markup=cancel
    )


@router.message(Command("terms"), StateFilter("*"))
async def handler_in_specific_state(message: Message, state: FSMContext):
    await message.delete()
    await state.clear()
    return await bot.send_message(
        chat_id=message.chat.id, text=terms, reply_markup=cancel, protect_content=True
    )


@router.message(Command("privacy"), StateFilter("*"))
async def handler_in_specific_state(message: Message, state: FSMContext):
    await message.delete()
    await state.clear()
    return await bot.send_message(
        chat_id=message.chat.id, text=privacy, reply_markup=cancel, protect_content=True
    )
