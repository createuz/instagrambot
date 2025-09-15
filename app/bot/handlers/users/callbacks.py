# app/bot/handlers/callbacks.py
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from app.bot.handlers.users.kb import get_add_to_group
from app.bot.handlers.users.translations import t
from app.bot.utils import LanguageSelection
from app.core.logger import get_logger
from app.db.services.redis_manager import RedisManager
from app.db.services.user_service import upsert_user_language, redis_set_lang

router = Router()


@router.callback_query(F.data.startswith("lang:"), LanguageSelection.select_language)
async def lang_callback(call: CallbackQuery, state: FSMContext, **data):
    db = data.get("db")
    rid = data.get("request_id")
    logger = get_logger(rid)
    redis = RedisManager.client()
    lang = call.data.split(":", 1)[1].strip()
    tg_id = call.from_user.id
    try:
        user_id = await upsert_user_language(session=db, chat_id=tg_id, language=lang)
        if getattr(db, "session_created", False):
            db.info["committed_by_handler"] = True
            await db.commit()
        logger.info("lang_callback: upserted id=%s chat_id=%s lang=%s", user_id, tg_id, lang)
    except Exception:
        try:
            if getattr(db, "session_created", False):
                await db.rollback()
        except Exception:
            logger.exception("rollback failed")
        await call.answer("Server error, try again later.", show_alert=True)
        return await state.clear()
    try:
        if redis:
            await redis_set_lang(redis, tg_id, lang)
    except Exception:
        logger.warning("redis set failed for %s", tg_id)

    await call.answer(f'✅ {lang}')
    try:
        await call.message.edit_text(
            text=t(lang, "start"),
            reply_markup=get_add_to_group(lang),
            disable_web_page_preview=True
        )
    except Exception:
        logger.warning("edit message failed")
    return await state.clear()
