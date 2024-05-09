import asyncio
import time
from data import *
from db.models import User, Group


async def send_message_all(chat_id: int, text=None, video=None, photo=None, caption=None, keyboard=None):
    try:
        if text:
            await bot.send_message(
                chat_id=chat_id,
                text=f"<b>{text}</b>",
                reply_markup=keyboard,
                disable_web_page_preview=True
            )
        if video:
            await bot.send_video(
                chat_id=chat_id,
                video=video,
                caption=f"<b>{caption}</b>",
                reply_markup=keyboard
            )
        if photo:
            await bot.send_photo(
                chat_id=chat_id,
                photo=photo,
                caption=f"<b>{caption}</b>",
                reply_markup=keyboard
            )
        return True
    except Exception as e:
        return None


async def send_messages_to_users(user_ids: list, text=None, video=None, photo=None, caption=None, keyboard=None):
    try:
        active_count = 0
        no_active_count = 0
        for user_id in user_ids:
            if await send_message_all(
                    chat_id=user_id,
                    text=text,
                    video=video,
                    photo=photo,
                    caption=caption,
                    keyboard=keyboard
            ):
                active_count += 1
            else:
                no_active_count += 1
            await asyncio.sleep(0.04)
        return active_count, no_active_count
    except Exception as e:
        return None


async def send_messages_to_groups(group_ids: list, text=None, video=None, photo=None, caption=None, keyboard=None):
    try:
        active_count = 0
        no_active_count = 0
        for group_id in group_ids:
            if await send_message_all(
                    chat_id=group_id,
                    text=text,
                    video=video,
                    photo=photo,
                    caption=caption,
                    keyboard=keyboard
            ):
                active_count += 1
            else:
                no_active_count += 1
            await asyncio.sleep(0.04)
        return active_count, no_active_count
    except Exception as e:
        return None


async def send_message_admin(text: object = None, video: object = None, photo: object = None, caption: object = None,
                             keyboard: object = None) -> object:
    try:
        if text:
            return await bot.send_message(
                chat_id=ADMINS[0],
                text=f"<b>{text}</b>",
                reply_markup=keyboard,
                disable_web_page_preview=True
            )
        if video:
            return await bot.send_video(
                chat_id=ADMINS[0],
                video=video,
                caption=f"<b>{caption}</b>",
                reply_markup=keyboard
            )
        if photo:
            return await bot.send_photo(
                chat_id=ADMINS[0],
                photo=photo,
                caption=f"<b>{caption}</b>",
                reply_markup=keyboard
            )
    except Exception as e:
        return None


async def admin_send_message_all(text=None, video=None, photo=None, caption=None, keyboard=None):
    try:
        admin_lang = await User.get_language(chat_id=int(ADMINS[0]))
        start_time = time.time()
        all_user_ids = await User.get_all_users(admin_lang=admin_lang)
        all_group_ids = await Group.get_all_groups(admin_lang=admin_lang)
        active_users, no_active_users = await send_messages_to_users(
            user_ids=all_user_ids,
            text=text,
            video=video,
            photo=photo,
            caption=caption,
            keyboard=keyboard
        )
        active_groups, no_active_groups = await send_messages_to_groups(
            group_ids=all_group_ids,
            text=text,
            video=video,
            photo=photo,
            caption=caption,
            keyboard=keyboard
        )
        elapsed_time = time.time() - start_time
        date = format_time(elapsed_time=elapsed_time)
        date2 = time.strftime("%H:%M:%S", time.gmtime(elapsed_time))
        msg = f'''┏━━━━━━━━━━━━━━━━━━━━━━━━
┃  📊  Sent message Statistic
┣━━━━━━━━━━━━━━━━━━━━━━━━
┃
┃  •  All users:  {len(all_user_ids)}
┃
┃  •  Active users:  {active_users}
┃
┃  •  No active users:  {no_active_users}
┃
┃  •  All groups:  {len(all_group_ids)}
┃
┃  •  Active groups:  {active_groups}
┃
┃  •  No active groups:  {no_active_groups}
┃
┃  •  Total time1:  {date}
┃
┃  •  Total time2:  {date2}
┃
┃  •  Powered by:  @{BOT_USERNAME}
┃
┗━━━━━━━━━━━━━━━━━━━━━━━━'''
        await bot.send_message(chat_id=ADMINS[0], text=f"<b>{msg}</b>")
        await bot.send_message(chat_id='-1002073628577', text=f"<b>{msg}</b>")
    except Exception as e:
        await bot.send_message(chat_id=ADMINS[0], text=f"Xatolik yuz berdi: {str(e)}")
