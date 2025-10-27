# handlers/admins/broadcast.py
import asyncio
from typing import Any, Dict

from aiogram import Router, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from old.bot.handlers.admins.keyboards import create_keyboard
from old.core.logger import get_logger
from old.db.sessions.session import AsyncSessionLocal
from old.bot.handlers.admins.broadcast_integrated import BroadcastManager

logger = get_logger()
router = Router()

# single manager instance (reuse)
broadcast_manager = BroadcastManager(
    session_maker=AsyncSessionLocal,
    bot=None,  # set in handler runtime
    rate=20.0,
    concurrency=50,
    batch_size=2000,
    max_retries=5,
)


@router.message(Command("broadcast_preview"))
async def broadcast_preview_handler(
    message: Message, state: FSMContext, bot: Bot, **data: Any
):
    admin_id = message.from_user.id
    st = await state.get_data()
    caption = st.get("caption", "")
    media_type = st.get("media_type", "text")
    buttons = st.get("buttons", [])
    keyboard = create_keyboard(buttons)

    try:
        if media_type == "text":
            await bot.send_message(
                chat_id=admin_id, text=caption, reply_markup=keyboard
            )
        elif media_type == "photo":
            await bot.send_photo(
                chat_id=admin_id,
                photo=st.get("media"),
                caption=caption,
                reply_markup=keyboard,
            )
        elif media_type == "video":
            await bot.send_video(
                chat_id=admin_id,
                video=st.get("media"),
                caption=caption,
                reply_markup=keyboard,
            )
        await message.answer(
            "Agar hamma narsa toʻgʻri bo'lsa, /broadcast_confirm buyrug'i bilan tasdiqlang."
        )
    except Exception as e:
        logger.exception("Preview send failed: %s", e)
        await message.answer("Preview yuborishda xatolik yuz berdi.")


@router.message(Command("broadcast_confirm"))
async def broadcast_confirm_handler(
    message: Message, state: FSMContext, bot: Bot, **data: Any
):
    admin_id = message.from_user.id
    st = await state.get_data()
    payload: Dict[str, Any] = {
        "media_type": st.get("media_type", "text"),
        "caption": st.get("caption"),
        "media": st.get("media"),
        "reply_markup": create_keyboard(st.get("buttons", [])),
        "extra_kwargs": st.get("extra_kwargs", {}) or {},
        "disable_web_page_preview": st.get("disable_web_page_preview", True),
    }

    # ensure manager has bot
    if broadcast_manager.bot is None:
        broadcast_manager.bot = bot

    async def _run_and_log():
        try:
            logger.info("Broadcast started by admin %s", admin_id)
            stats = await broadcast_manager.broadcast(
                payload=payload, admin_chat_id=admin_id
            )
            logger.info("Broadcast finished (admin=%s) stats=%s", admin_id, stats)
        except Exception as e:
            logger.exception("Broadcast task exception: %s", e)
            try:
                await bot.send_message(
                    chat_id=admin_id, text=f"Broadcast failed with exception: {e}"
                )
            except Exception:
                logger.exception("Failed to notify admin about broadcast failure")

    # run background task
    asyncio.create_task(_run_and_log())

    await message.answer("Broadcast boshlandi. Tugaganida hisobot yuboriladi.")
    await state.clear()
