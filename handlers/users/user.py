import platform
import subprocess
import time
from datetime import timedelta

import psutil
import speedtest
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
            await bot.send_message(chat_id=message.chat.id, text=choose_button, reply_markup=get_language_keyboard())
            parts = message.text.split()
            added_by = parts[1] if len(parts) > 1 else 'true'
            await state.update_data(added_by=added_by)
            await state.set_state(LanguageSelection.select_language)
        else:
            await bot.send_message(
                chat_id=message.chat.id,
                text=langs_text[language]['start'],
                reply_markup=get_add_to_group()[language],
                disable_web_page_preview=True
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
        await bot.send_message(chat_id=message.chat.id, text=choose_button, reply_markup=get_language_keyboard())
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
    await bot.send_message(chat_id=message.chat.id, text=langs_text[language]['help'], reply_markup=cancel)
    await state.clear()


@user_router.message(Command("terms"), StateFilter('*'))
async def handler_in_specific_state(message: Message, state: FSMContext):
    await message.delete()
    await bot.send_message(chat_id=message.chat.id, text=terms, reply_markup=cancel)
    await state.clear()


@user_router.message(Command("privacy"), StateFilter('*'))
async def handler_in_specific_state(message: Message, state: FSMContext):
    await message.delete()
    await bot.send_message(chat_id=message.chat.id, text=privacy, reply_markup=cancel)
    await state.clear()


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


@user_router.message(Command("server"))
async def send_server_info(message: Message):
    await message.answer("⏳ <b>Server haqida ma'lumotlar olinmoqda...</b>", parse_mode="HTML")
    info = get_system_info()
    await message.answer(info, parse_mode="HTML")
