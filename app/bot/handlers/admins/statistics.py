# handlers/admins/panel.py
import time
from typing import Optional

from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy import select, func

from app.bot.utils import IsAdmin
from app.core.config import bot
from app.db.models.user import User
from app.db.services.user_repo import UserRepo
from app.db.sessions.session import logger

panel_router = Router()

from app.bot.handlers.admins.kb import update_user_stat, stat_menu, statistic_lang

BOT_START_TIME = time.time()


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
