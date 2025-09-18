import asyncio
import time
from typing import Optional, List, Tuple

from aiogram.fsm.context import FSMContext

from app.bot.handlers.admins.keyboards import create_keyboard, confirm_options
from app.bot.utils import AdsStates
from app.core.config import bot, ADMIN
from app.db.services.user_repo import UserRepo


async def send_message_all(chat_id: int, state: FSMContext) -> Optional[bool]:
    try:
        data = await state.get_data()
        keyboard = create_keyboard(data["buttons"])
        if data["media_type"] == "text":
            await bot.send_message(
                chat_id=chat_id,
                text=data["caption"],
                reply_markup=keyboard,
                disable_web_page_preview=True
            )
        if data["media_type"] == "photo":
            await bot.send_photo(
                chat_id=chat_id,
                photo=data["media"],
                caption=data["caption"],
                reply_markup=keyboard
            )
        if data["media_type"] == "video":
            await bot.send_video(
                chat_id=chat_id,
                video=data["media"],
                caption=data["caption"],
                reply_markup=keyboard
            )
        if data["media_type"] == "video_note":
            await bot.send_video_note(
                chat_id=chat_id,
                video_note=data["media"],
                reply_markup=keyboard
            )
        if data["media_type"] == "animation":
            await bot.send_animation(
                chat_id=chat_id,
                animation=data["media"],
                caption=data["caption"],
                reply_markup=keyboard
            )
        return True
    except Exception:
        return None


async def send_message_users(user_ids: List[int], state: FSMContext) -> Optional[Tuple[int]]:
    try:
        active_users = 0
        inactive_users = 0
        for user_id in user_ids:
            if await send_message_all(chat_id=user_id, state=state):
                active_users += 1
            else:
                inactive_users += 1
            await asyncio.sleep(0.04)
        return active_users, inactive_users
    except Exception:
        return None


async def send_message_admin(state: FSMContext):
    try:
        data = await state.get_data()
        keyboard = create_keyboard(data["buttons"])
        if data["media_type"] == "text":
            await bot.send_message(
                chat_id=ADMIN,
                text=data["caption"],
                reply_markup=keyboard,
                disable_web_page_preview=True
            )
        if data["media_type"] == "photo":
            await bot.send_photo(
                chat_id=ADMIN,
                photo=data["media"],
                caption=data["caption"],
                reply_markup=keyboard
            )
        if data["media_type"] == "video":
            await bot.send_video(
                chat_id=ADMIN,
                video=data["media"],
                caption=data["caption"],
                reply_markup=keyboard
            )
        if data["media_type"] == "video_note":
            await bot.send_video_note(
                chat_id=ADMIN,
                video_note=data["media"],
                reply_markup=keyboard
            )
        if data["media_type"] == "animation":
            await bot.send_animation(
                chat_id=ADMIN,
                animation=data["media"],
                caption=data["caption"],
                reply_markup=keyboard
            )
        await bot.send_message(chat_id=ADMIN, text="Postni yuborishni tasdiqlaysizmi?", reply_markup=confirm_options())
        await state.set_state(AdsStates.confirm_send)
    except Exception as e:
        await bot.send_message(chat_id=ADMIN, text=f"Postni yuborishda xatolik: {str(e)}")
        await state.clear()
        return None


async def admin_send_message_all(state: FSMContext):
    try:
        admin_lang = await UserRepo.get_language(chat_id=int(ADMIN))
        start_time = time.time()
        total_users = await UserRepo.get_all_users(admin_lang=admin_lang)
        active_users, inactive_users = await send_message_users(user_ids=total_users, state=state)
        end_time = time.time()
        msg = f'''┏━━━━━━━━━━━━━━━━━━━━━━━━
┃  ✦  Sent message Statistic
┣━━━━━━━━━━━━━━━━━━━━━━━━
┃
┃ ✦ All users:  {len(total_users)}
┃
┃ ✦ Active users:  {active_users}
┃
┃ ✦ Inactive users:  {inactive_users}
┃ 
┃ ✦ Success rate:  {active_users / len(total_users) * 100:.2f}%
┃
┃ ✦ Start time:  {time.strftime("%H:%M:%S", time.gmtime(start_time))}
┃ 
┃ ✦ End time:  {time.strftime("%H:%M:%S", time.gmtime(end_time))}
┃ 
┃ ✦ Total time:  {time.strftime("%H:%M:%S", time.gmtime(end_time - start_time))}
┃
┗━━━━━━━━━━━━━━━━━━━━━━━━'''
        await bot.send_message(chat_id=ADMIN, text=f"<b>{msg}</b>")
    except Exception as e:
        await bot.send_message(chat_id=ADMIN, text=f"Xatolik yuz berdi: {str(e)}")
