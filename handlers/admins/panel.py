import json
import os
import platform
import subprocess
import time
from collections import Counter
from datetime import timedelta

import psutil
import speedtest
from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, FSInputFile
from sqlalchemy import select

from data import bot, logger, AddAdmin, IsAdmin
from db import Admin, User, db

panel_router = Router()

from .kb import admin_menu, update_user_stat, stat_menu, home_menu, statistic_lang


@panel_router.message(Command("admin"), IsAdmin(), StateFilter('*'))
async def show_admin_panel(message: Message):
    await message.delete()
    await bot.send_message(chat_id=message.chat.id, text="<b>⚙ Welcome to Admin Panel</b>", reply_markup=home_menu())


@panel_router.callback_query(F.data == "home_menu", IsAdmin())
async def return_to_menu(call: CallbackQuery):
    await bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="<b>⚙ Welcome to Admin Panel</b>",
        reply_markup=home_menu()
    )


@panel_router.callback_query(F.data == "admin_menu", IsAdmin())
async def show_admin_menu(call: CallbackQuery):
    await bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="<b>🅰 Admin Menu</b>",
        reply_markup=admin_menu()
    )


@panel_router.callback_query(F.data == "admins_data", IsAdmin())
async def admin_data_handler(call: CallbackQuery):
    try:
        data = await Admin.get_admins_data()
        if data:
            admin_data = "\n".join(
                f"┃ ID: <code>{user.chat_id}</code> ┃ <a href='tg://user?id={user.chat_id}'>{user.first_name}</a>"
                for user in data
            )
            data_msg = f"""
┏━━━━━━━━━━━━━━━━━━━━━
┃ 🅰 Admin Statistic
┣━━━━━━━━━━━━━━━━━━━━━
{admin_data}
┗━━━━━━━━━━━━━━━━━━━━━"""
            await bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=f"<b>{data_msg}</b>"
            )
        else:
            await bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text="<b>🛑 Hozirda Admin ma'lumotlari mavjud emas.</b>")
    except Exception as e:
        logger.exception("Error: %s", e)


@panel_router.callback_query(F.data == "add_admin", IsAdmin())
async def add_admin_handler(call: CallbackQuery, state: FSMContext):
    await bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="Yangi adminning chat ID sini kiriting:"
    )
    await state.set_state(AddAdmin.waiting_for_add_chat_id)


@panel_router.message(AddAdmin.waiting_for_add_chat_id)
async def save_new_admin(message: Message, state: FSMContext):
    try:
        chat_id, username, first_name = await User.get_user(message.text)
        await Admin.create_admin(chat_id=chat_id, username=username, first_name=first_name)
        await message.answer(f"<b>{first_name}</b> adminlar ro'yxatiga qo'shildi ✅", reply_markup=admin_menu())
        await state.clear()
    except Exception as e:
        await message.answer(f"❌ Xatolik yuz berdi: {str(e)}")


@panel_router.callback_query(F.data == "del_admin", IsAdmin())
async def delete_admin_handler(call: CallbackQuery, state: FSMContext):
    await bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="O'chirmoqchi bo'lgan adminning Chat ID sini kiriting:"
    )
    await state.set_state(AddAdmin.waiting_for_del_chat_id)


@panel_router.message(AddAdmin.waiting_for_del_chat_id)
async def save_deleted_admin(message: Message, state: FSMContext):
    try:
        await Admin.delete_admin(message.text)
        await message.answer(f"Chat ID: <b>{message.text}</b> adminlar ro'yxatidan chiqarildi ✅",
                             reply_markup=admin_menu())
        await state.clear()
    except Exception as e:
        await message.answer(f"❌ Xatolik yuz berdi: {str(e)}")


@panel_router.callback_query(F.data == "stat_menu", IsAdmin())
async def chose_statistics(call: CallbackQuery):
    await bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="<b>📊 Statistikani tanlang:</b>",
        reply_markup=stat_menu()
    )


async def user_statistics():
    try:
        async with db.get_session() as session:
            users = await session.execute(select(User.language))
            lang_count_user = Counter([language for language, in users])
            total_users = sum(lang_count_user.values()) or 1
            max_lang_length = max(len(name) for name in statistic_lang.values())
            max_count_length = max(len(str(count)) for count in lang_count_user.values()) if lang_count_user else 1
            sorted_langs = sorted(statistic_lang.items(), key=lambda x: lang_count_user.get(x[0], 0), reverse=True)
            user_data = "\n".join(
                f"<b>┃ {language_name.ljust(max_lang_length)}:  {str(lang_count_user.get(language_code, 0)).rjust(max_count_length)}</b>  {lang_count_user.get(language_code, 0) / total_users * 100:5.1f}%"
                for language_code, language_name in sorted_langs
            )
            today = await User.joined_last_24_hours()
            month = await User.joined_last_month()
            return f"""<b>
┏━━━━━━━━━━━━━━━━━━━━━
┃ ✦  ᴜꜱᴇʀꜱ ꜱᴛᴀᴛɪꜱᴛɪᴄ
┣━━━━━━━━━━━━━━━━━━━━━
┃ ✦  ᴊᴏɪɴᴇᴅ ᴛᴏᴅᴀʏ:  {today}
┃
┃ ✦  ᴊᴏɪɴᴇᴅ ᴛʜɪꜱ ᴍᴏɴᴛʜ:  {month}
┃
┃ ✦  ᴀʟʟ ᴜꜱᴇʀꜱ ᴄᴏᴜɴᴛ:  {total_users}
┣━━━━━━━━━━━━━━━━━━━━━</b>
{user_data}<b>
┗━━━━━━━━━━━━━━━━━━━━━</b>"""
    except Exception as e:
        logger.exception("Error: %s", e)
        return None


@panel_router.callback_query(F.data == "user_stat", IsAdmin())
async def total_user_statistics(call: CallbackQuery):
    try:
        user_stat = await user_statistics()
        await bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=user_stat,
            reply_markup=update_user_stat()
        )
    except Exception as e:
        logger.exception("Error: %s", e)


@panel_router.callback_query(F.data == "update_user_stat", IsAdmin())
async def total_user_statistics(call: CallbackQuery):
    try:
        user_stat = await user_statistics()
        await bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=user_stat,
            reply_markup=update_user_stat()
        )
    except Exception as e:
        logger.exception("Error: %s", e)


@panel_router.callback_query(F.data == "chat_ids", IsAdmin())
async def chat_ids_handler(call: CallbackQuery):
    try:
        users = await User.get_all_users()
        file_path = 'users.json'
        with open(file_path, 'w', encoding='utf-8') as users_file:
            json.dump(users, users_file, indent=3, ensure_ascii=False)
        user_msg = f"""<b>
📄 Users count: {len(users)}

🤖 Bot: @</b>"""
        document = FSInputFile(file_path)
        await bot.send_document(chat_id=call.message.chat.id, document=document, caption=user_msg)
        os.remove(file_path)
    except Exception as e:
        logger.exception("Unexpected error: %s", e)


@panel_router.callback_query(F.data == "cancel", StateFilter('*'))
async def cancel_admin_action(call: CallbackQuery, state: FSMContext):
    try:
        await call.message.delete()
        await call.answer("Bekor qilindi ✅")
        await state.clear()
    except Exception as e:
        logger.exception("Xatolik: %s", e)


@panel_router.message(Command('break'), IsAdmin(), StateFilter('*'))
async def stop_message_sending(message: Message, state: FSMContext):
    try:
        await message.answer("⚙ Xabar yuborish to‘xtatildi")
        await state.clear()
    except Exception as e:
        await state.clear()
        await message.answer(f"❌ Xatolik yuz berdi: {str(e)}")


BOT_START_TIME = time.time()


def get_ping():
    try:
        ping_cmd = ["ping", "-c", "4", "google.com"] if platform.system() != "Windows" else ["ping", "-n", "4",
                                                                                             "google.com"]
        result = subprocess.run(ping_cmd, capture_output=True, text=True)
        output = result.stdout.split("\n")[-2]
        ping_time = output.split("/")[-3] if "/" in output else "Noma'lum"
        return f"📶 Ping: <b>{ping_time} ms</b>"
    except Exception:
        return "📶 Ping olinmadi"


def get_speed():
    try:
        st = speedtest.Speedtest()
        st.get_best_server()
        download_speed = st.download() / 1e6
        upload_speed = st.upload() / 1e6
        return f"🚀 <b>Internet tezligi:</b>\n🔻 Yuklab olish: <b>{download_speed:.2f} Mbps</b>\n🔺 Yuklash: <b>{upload_speed:.2f} Mbps</b>"
    except Exception:
        return "🚀 Internet tezligi aniqlanmadi"


def get_uptime():
    uptime_seconds = time.time() - psutil.boot_time()
    bot_uptime_seconds = time.time() - BOT_START_TIME
    return (
        f"⏳ <b>Server Uptime:</b> {str(timedelta(seconds=int(uptime_seconds)))}\n"
        f"🤖 <b>Bot Uptime:</b> {str(timedelta(seconds=int(bot_uptime_seconds)))}"
    )


def format_size(bytes):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes < 1024.0:
            return f"{bytes:.2f} {unit}"
        bytes /= 1024.0
    return f"{bytes:.2f} PB"


def get_system_info():
    try:
        uname = platform.uname()
        virtual_memory = psutil.virtual_memory()
        disk_usage = psutil.disk_usage("/")

        system_info = (
            f"🖥 <b>Server Ma'lumotlari:</b>\n"
            f"🔹 Tizim: <b>{uname.system}</b>\n"
            f"🔹 Host: <b>{uname.node}</b>\n"
            f"🔹 OS: <b>{uname.release}</b>\n"
            f"🔹 Arxitektura: <b>{uname.machine}</b>\n"
            f"🔹 Processor: <b>{uname.processor}</b>\n"
        )

        cpu_info = (
            f"\n⚙️ <b>CPU Ma'lumotlari:</b>\n"
            f"🖥 Yadro: <b>{psutil.cpu_count(logical=True)}</b>\n"
            f"📊 CPU Yuklanishi: <b>{psutil.cpu_percent()}%</b>\n"
        )

        ram_info = (
            f"\n💾 <b>RAM:</b>\n"
            f"📌 Jami: <b>{format_size(virtual_memory.total)}</b>\n"
            f"📊 Ishlatilmoqda: <b>{format_size(virtual_memory.used)}</b>\n"
            f"🟢 Bo‘sh: <b>{format_size(virtual_memory.available)}</b>\n"
            f"📈 Yuklanish: <b>{virtual_memory.percent}%</b>\n"
        )

        disk_info = (
            f"\n🗄 <b>Disk:</b>\n"
            f"💾 Umumiy: <b>{format_size(disk_usage.total)}</b>\n"
            f"📂 Ishlatilgan: <b>{format_size(disk_usage.used)}</b>\n"
            f"🟢 Bo‘sh joy: <b>{format_size(disk_usage.free)}</b>\n"
            f"📊 Yuklanish: <b>{disk_usage.percent}%</b>\n"
        )

        return system_info + cpu_info + ram_info + disk_info + f"\n{get_ping()}\n{get_speed()}\n\n{get_uptime()}"
    except Exception as e:
        return f"🚨 Xatolik yuz berdi: {str(e)}"


@panel_router.message(Command("server"))
async def send_server_info(message: Message):
    await message.answer("⏳ <b>Server haqida ma'lumotlar olinmoqda...</b>", parse_mode="HTML")
    info = get_system_info()
    await message.answer(info, parse_mode="HTML")
