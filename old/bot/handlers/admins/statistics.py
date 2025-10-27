# handlers/admins/panel.py
import json
import time
from typing import Optional, Dict, Any

from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy import select, func

from old.bot.handlers.admins.keyboards import (
    update_user_stat,
    stat_menu,
    statistic_lang,
)
from old.bot.utils import IsAdmin
from old.core.config import bot  # conf must have redis_url (optional)
from old.core.logger import get_logger
from old.db.models.user import User
from old.db.services.redis_manager import RedisManager
from old.db.services.user_repo import UserRepo
from old.db.sessions.session import AsyncSessionLocal

logger = get_logger()
repo = UserRepo(logger=logger)

router = Router()
STATS_CACHE_KEY = "stats"
STATS_TTL = 10 * 60  # 10 minutes


@router.callback_query(F.data == "stat_menu", IsAdmin())
async def chose_statistics(call: CallbackQuery):
    await call.message.edit_text(
        text="<b>📊 Statistikani tanlang:</b>", reply_markup=stat_menu()
    )


@router.callback_query(F.data.in_(("user_stat", "update_user_stat")), IsAdmin())
async def total_user_statistics(call: CallbackQuery):
    _redis_client = RedisManager.client()
    try:
        # Try Redis cache first
        cached = None
        if _redis_client is not None:
            try:
                cached = await _redis_client.get(STATS_CACHE_KEY)
            except Exception:
                logger.warning("Redis get failed for stats cache")
                cached = None

        if cached:
            # cached is JSON string
            try:
                stats_obj = json.loads(cached)
                text = _format_stats_text(stats_obj)
                await call.message.edit_text(text=text, reply_markup=update_user_stat())
                return
            except Exception:
                logger.exception("Failed to parse cached stats; will recompute")

        # No cache -> compute
        stats_obj = await _compute_stats_and_counts()
        if not stats_obj:
            await bot.answer_callback_query(call.id, "Statistika olinmadi.")
            return

        # store in redis
        if _redis_client is not None:
            try:
                await _redis_client.set(
                    STATS_CACHE_KEY, json.dumps(stats_obj), ex=STATS_TTL
                )
            except Exception:
                logger.warning("Redis set failed for stats cache")

        text = _format_stats_text(stats_obj)
        await call.message.edit_text(text=text, reply_markup=update_user_stat())

    except Exception:
        logger.exception("total_user_statistics error")
        await bot.answer_callback_query(
            call.id, "Server xatoligi — keyinroq urinib ko'ring."
        )


async def _compute_stats_and_counts() -> Optional[Dict[str, Any]]:
    """
    Compute stats:
      - counts per language (all users)
      - total users (exact count)
      - joined last 24h and last 30 days (repo helpers)
    Returns a JSON-serializable dict.
    """
    try:
        async with AsyncSessionLocal() as session:
            # 1) counts by language (ALL users, no is_active filter)
            stmt = select(User.language, func.count().label("cnt")).group_by(
                User.language
            )
            res = await session.execute(stmt)
            rows = res.all()  # small: number of languages

            lang_count: Dict[str, int] = {}
            total_users = 0
            for lang, cnt in rows:
                key = lang if lang is not None else "unknown"
                lang_count[key] = int(cnt)
                total_users += int(cnt)

            # 2) total users - ensure exact (if rows empty, fallback to count)
            if total_users == 0:
                # if no grouped rows (unlikely), fallback to explicit count
                total_res = await session.execute(select(func.count(User.chat_id)))
                total_users = int(total_res.scalar_one_or_none() or 0)

            # 3) joined counts using repo helpers (they expect session param)
            joined_24h = await repo.joined_last_24h(session)
            joined_month = await repo.joined_last_month(session)

        return {
            "generated_at": int(time.time()),
            "total_users": total_users,
            "lang_count": lang_count,
            "joined_24h": joined_24h,
            "joined_month": joined_month,
        }
    except Exception:
        logger.exception("_compute_stats_and_counts failed")
        return None


def _format_stats_text(stats_obj: Dict[str, Any]) -> str:
    total_users = stats_obj.get("total_users", 0)
    lang_count = stats_obj.get("lang_count", {}) or {}
    joined_24h = stats_obj.get("joined_24h", 0)
    joined_month = stats_obj.get("joined_month", 0)
    denom = total_users if total_users > 0 else 1
    codes_sorted = sorted(
        statistic_lang.keys(), key=lambda c: lang_count.get(c, 0), reverse=True
    )
    display_labels = [statistic_lang[c] for c in codes_sorted]
    max_label_len = max((len(lbl) for lbl in display_labels), default=2)
    max_count_len = max(
        (len(str(lang_count.get(c, 0))) for c in codes_sorted), default=1
    )

    lines = []
    for code in codes_sorted:
        label = statistic_lang.get(code, code)
        count = lang_count.get(code, 0)
        pct = (count / denom) * 100
        lines.append(
            f"┃ {label.ljust(max_label_len)} : {str(count).rjust(max_count_len)}   {pct:5.1f}%"
        )
    header = (
        "<b>\n"
        "┏━━━━━━━━━━━━━━━━━━━━━\n"
        "┃ ✦  ᴜꜱᴇʀꜱ ꜱᴛᴀᴛɪꜱᴛɪᴄ\n"
        "┣━━━━━━━━━━━━━━━━━━━━━\n"
        f"┃ ✦  ᴊᴏɪɴᴇᴅ ᴛᴏᴅᴀʏ:  {joined_24h}\n\n"
        f"┃ ✦  ᴊᴏɪɴᴇᴅ ᴛʜɪꜱ ᴍᴏɴᴛʜ:  {joined_month}\n\n"
        f"┃ ✦  ᴀʟʟ ᴜꜱᴇʀꜱ ᴄᴏᴜɴᴛ:  {total_users}\n"
        "┣━━━━━━━━━━━━━━━━━━━━━</b>\n"
    )
    body = (
        "\n".join(lines) if lines else "<b>┃ Hech qanday foydalanuvchi topilmadi.</b>"
    )
    footer = "<b>\n┗━━━━━━━━━━━━━━━━━━━━━━━━━</b>"
    return header + body + "\n" + footer
