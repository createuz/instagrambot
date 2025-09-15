# handlers/admins/panel.py
import time

from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.bot.utils import IsAdmin, AddAdmin
from app.core.config import bot
from app.db.models.admin import Admin
from app.db.services.user_repo import UserRepo
from app.db.sessions.session import logger

panel_router = Router()

from app.bot.handlers.admins.kb import admin_menu, home_menu

BOT_START_TIME = time.time()


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
