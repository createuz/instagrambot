# handlers/admins/panel.py
import time
from typing import Optional

from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy import select, func

from app.bot.utils import IsAdmin, AddAdmin
from app.core.config import bot
from app.db.models.admin import Admin
from app.db.models.user import User
from app.db.services.user_repo import UserRepo
from app.db.sessions.session import logger

panel_router = Router()

from app.bot.handlers.admins.kb import admin_menu, update_user_stat, stat_menu, home_menu, statistic_lang

BOT_START_TIME = time.time()


# -------------------- DB / Stats helpers --------------------
async def user_statistics() -> Optional[str]:
    try:
        async with db.get_session() as session:
            stmt = select(User.language, func.count()).group_by(User.language)
            res = await session.execute(stmt)
            rows = res.all()  # list of tuples (language, count)
            lang_count = {lang if lang is not None else "unknown": cnt for lang, cnt in rows}
            total_users = sum(lang_count.values()) or 1

            max_lang_len = max((len(name) for name in statistic_lang.values()), default=2)
            max_count_len = max((len(str(v)) for v in lang_count.values()), default=1)

            sorted_langs = sorted(statistic_lang.items(), key=lambda kv: lang_count.get(kv[0], 0), reverse=True)

            lines = []
            for code, display in sorted_langs:
                count = lang_count.get(code, 0)
                pct = count / total_users * 100
                lines.append(f"<b>┃ {display.ljust(max_lang_len)}: {str(count).rjust(max_count_len)}</b>  {pct:5.1f}%")

            today = await UserRepo.joined_last_24h()
            month = await UserRepo.joined_last_month()

            header = (
                "<b>\n"
                "┏━━━━━━━━━━━━━━━━━━━━━\n"
                "┃ ✦  ᴜꜱᴇʀꜱ ꜱᴛᴀᴛɪꜱᴛɪᴄ\n"
                "┣━━━━━━━━━━━━━━━━━━━━━\n"
                f"┃ ✦  ᴊᴏɪɴᴇᴅ ᴛᴏᴅᴀʏ:  {today}\n\n"
                f"┃ ✦  ᴊᴏɪɴᴇᴅ ᴛʜɪꜱ ᴍᴏɴᴛʜ:  {month}\n\n"
                f"┃ ✦  ᴀʟʟ ᴜꜱᴇʀꜱ ᴄᴏᴜɴᴛ:  {total_users}\n"
                "┣━━━━━━━━━━━━━━━━━━━━━</b>\n"
            )

            body = "\n".join(lines)
            footer = "<b>\n┗━━━━━━━━━━━━━━━━━━━━━</b>"
            return header + body + "\n" + footer

    except Exception as e:
        logger.exception("user_statistics error: %s", e)
        return None


@panel_router.message(Command("admin"), IsAdmin(), StateFilter('*'))
async def show_admin_panel(message: Message):
    await message.delete()
    await bot.send_message(chat_id=message.chat.id, text="<b>⚙ Welcome to Admin Panel</b>", reply_markup=home_menu())


@panel_router.callback_query(F.data == "home_menu", IsAdmin())
async def return_to_menu(call: CallbackQuery):
    await call.message.edit_text(text="<b>⚙ Welcome to Admin Panel</b>", reply_markup=home_menu())


@panel_router.callback_query(F.data == "admin_menu", IsAdmin())
async def show_admin_menu(call: CallbackQuery):
    await call.message.edit_text(text="<b>🅰 Admin Menu</b>", reply_markup=admin_menu())


@panel_router.callback_query(F.data == "admins_data", IsAdmin())
async def admin_data_handler(call: CallbackQuery):
    try:
        data = await Admin.get_admins_data()
        if not data:
            await call.message.edit_text(text="<b>🛑 Hozirda Admin ma'lumotlari mavjud emas.</b>")
            return

        admin_lines = []
        for user in data:
            name = user.first_name or "NoName"
            admin_lines.append(f"┃ ID: <code>{user.chat_id}</code> ┃ <a href='tg://user?id={user.chat_id}'>{name}</a>")

        data_msg = "\n".join(admin_lines)
        full = f"""
┏━━━━━━━━━━━━━━━━━━━━━
┃ 🅰 Admin Statistic
┣━━━━━━━━━━━━━━━━━━━━━
{data_msg}
┗━━━━━━━━━━━━━━━━━━━━━"""
        await call.message.edit_text(text=f"<b>{full}</b>")
    except Exception as e:
        logger.exception("admins_data error: %s", e)


@panel_router.callback_query(F.data == "add_admin", IsAdmin())
async def add_admin_handler(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text(text="Yangi adminning chat ID sini kiriting:")
    await state.set_state(AddAdmin.waiting_for_add_chat_id)


@panel_router.message(AddAdmin.waiting_for_add_chat_id)
async def save_new_admin(message: Message, state: FSMContext):
    try:
        chat_id, username, first_name = await UserRepo.get_user(message.text)
        await Admin.create_admin(chat_id=chat_id, username=username, first_name=first_name)
        await message.answer(f"<b>{first_name}</b> adminlar ro'yxatiga qo'shildi ✅", reply_markup=admin_menu())
        await state.clear()
    except Exception as e:
        logger.exception("save_new_admin error: %s", e)
        await message.answer(f"❌ Xatolik yuz berdi: {str(e)}")


@panel_router.callback_query(F.data == "del_admin", IsAdmin())
async def delete_admin_handler(call: CallbackQuery):
    await call.message.edit_text(text="O'chirmoqchi bo'lgan adminning Chat ID sini kiriting:")
    await call.message.delete_reply_markup()


@panel_router.message(AddAdmin.waiting_for_del_chat_id)
async def save_deleted_admin(message: Message, state: FSMContext):
    try:
        await Admin.delete_admin(message.text)
        await message.answer(f"Chat ID: <b>{message.text}</b> adminlar ro'yxatidan chiqarildi ✅",
                             reply_markup=admin_menu())
        await state.clear()
    except Exception as e:
        logger.exception("save_deleted_admin error: %s", e)
        await message.answer(f"❌ Xatolik yuz berdi: {str(e)}")


@panel_router.callback_query(F.data == "stat_menu", IsAdmin())
async def chose_statistics(call: CallbackQuery):
    await call.message.edit_text(text="<b>📊 Statistikani tanlang:</b>", reply_markup=stat_menu())


@panel_router.callback_query(F.data.in_(("user_stat", "update_user_stat")), IsAdmin())
async def total_user_statistics(call: CallbackQuery):
    try:
        user_stat = await user_statistics()
        if not user_stat:
            await bot.answer_callback_query(call.id, "Statistika olinmadi.")
            return
        await call.message.edit_text(text=user_stat, reply_markup=update_user_stat())
    except Exception as e:
        logger.exception("total_user_statistics error: %s", e)


@panel_router.callback_query(F.data == "cancel", StateFilter('*'))
async def cancel_admin_action(call: CallbackQuery, state: FSMContext):
    try:
        await call.message.delete()
        await call.answer("Bekor qilindi ✅")
        await state.clear()
    except Exception as e:
        logger.exception("cancel_admin_action error: %s", e)


@panel_router.message(Command('break'), IsAdmin(), StateFilter('*'))
async def stop_message_sending(message: Message, state: FSMContext):
    try:
        await message.answer("⚙ Xabar yuborish to‘xtatildi")
        await state.clear()
    except Exception as e:
        logger.exception("stop_message_sending error: %s", e)
        await state.clear()
        await message.answer(f"❌ Xatolik yuz berdi: {str(e)}")


@panel_router.message(Command("server"))
async def send_server_info(message: Message):
    try:
        await message.answer("⏳ <b>Server haqida ma'lumotlar olinmoqda...</b>", parse_mode="HTML")
        info = await gather_system_info()
        await message.answer(info, parse_mode="HTML")
    except Exception as e:
        logger.exception("send_server_info error: %s", e)
        await message.answer(f"🚨 Xatolik yuz berdi: {e}")
