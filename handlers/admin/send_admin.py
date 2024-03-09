from data import *
from keyboards import send_message_type, tasdiqlash
from utlis.models import User


async def send_message_admin(text: str = None, video=None, photo=None, caption: str = None, keyboard=None):
    try:
        chat_id = await User.get_language(chat_id=int(ADMINS[0]))
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
        return await bot.send_message(chat_id=ADMINS[0], text=send_message_type, reply_markup=tasdiqlash)
    except Exception as e:
        return None
