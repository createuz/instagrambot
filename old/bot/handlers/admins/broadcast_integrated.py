# old/utils/broadcast_integrated.py
import asyncio
import math
import time
from importlib import import_module
from typing import Any, AsyncIterator, Callable, Dict, Optional

from sqlalchemy import select, update
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.ext.asyncio import AsyncSession

from old.core.logger import get_logger
from old.db.models.user import User
from old.db.services.user_repo import UserRepo
from old.db.sessions.session import AsyncSessionLocal  # your session maker

# robust aiogram exceptions import (v3 and common variants)
_exc_module = None
for mod in ("aiogram.exceptions", "aiogram.utils.exceptions"):
    try:
        _exc_module = import_module(mod)
        break
    except Exception:
        _exc_module = None

if _exc_module is None:
    raise ImportError("Cannot import aiogram exceptions module. Is aiogram installed?")


def _get_exc(*names):
    for n in names:
        if hasattr(_exc_module, n):
            return getattr(_exc_module, n)
    return None


RetryAfter = _get_exc("RetryAfter", "TelegramRetryAfter", "TelegramRetryAfterError")
BotBlocked = _get_exc("BotBlocked")
ChatNotFound = _get_exc("ChatNotFound")
Unauthorized = _get_exc("Unauthorized", "TelegramUnauthorizedError")
TelegramAPIError = _get_exc("TelegramAPIError", "TelegramError")
if TelegramAPIError is None:
    raise ImportError("TelegramAPIError not found in aiogram exceptions module.")

logger = get_logger()
repo = UserRepo(logger=logger)


# ------------------ Keyset iterator (DB producer) ------------------
async def iter_user_chat_ids(session: AsyncSession, batch_size: int = 2000) -> AsyncIterator[int]:
    """
    Keyset pagination yielding chat_id one-by-one, only is_active users.
    """
    last_id = 0
    while True:
        stmt = (
            select(User.id, User.chat_id)
            .where(User.id > last_id)
            .where(User.is_active == True)
            .order_by(User.id)
            .limit(batch_size)
        )
        res = await session.execute(stmt)
        rows = res.all()
        if not rows:
            break
        for r in rows:
            yield r.chat_id
        last_id = rows[-1].id


# ------------------ Token-bucket global rate limiter ------------------
class TokenBucket:
    def __init__(self, rate: float, capacity: Optional[int] = None):
        self.rate = float(rate)
        self.capacity = capacity or math.ceil(self.rate)
        self._tokens = float(self.capacity)
        self._last = time.monotonic()
        self._lock = asyncio.Lock()

    async def consume(self, tokens: float = 1.0):
        while True:
            async with self._lock:
                now = time.monotonic()
                elapsed = now - self._last
                if elapsed > 0:
                    self._tokens = min(self.capacity, self._tokens + elapsed * self.rate)
                    self._last = now
                if self._tokens >= tokens:
                    self._tokens -= tokens
                    return
                need = tokens - self._tokens
                wait_for = need / self.rate
            await asyncio.sleep(min(max(wait_for, 0.01), 1.0))


# ------------------ Message sender ------------------
async def _send_via_bot(bot, chat_id: int, payload: Dict[str, Any]) -> None:
    mt = payload.get("media_type", "text")
    caption = payload.get("caption")
    reply_markup = payload.get("reply_markup")
    extra_kwargs = payload.get("extra_kwargs", {}) or {}
    media = payload.get("media", None)

    if mt == "text":
        await bot.send_message(
            chat_id=chat_id,
            text=caption or "",
            reply_markup=reply_markup,
            disable_web_page_preview=payload.get("disable_web_page_preview", True),
            **extra_kwargs
        )
    elif mt == "photo":
        if media is None:
            raise ValueError("photo media is missing in payload")
        await bot.send_photo(
            chat_id=chat_id,
            photo=media,
            caption=caption or "",
            reply_markup=reply_markup,
            **extra_kwargs
        )
    elif mt == "video":
        if media is None:
            raise ValueError("video media is missing in payload")
        await bot.send_video(
            chat_id=chat_id,
            video=media,
            caption=caption or "", reply_markup=reply_markup,
            **extra_kwargs
        )
    elif mt == "animation":
        if media is None:
            raise ValueError("animation media is missing in payload")
        await bot.send_animation(
            chat_id=chat_id,
            animation=media,
            caption=caption or "", reply_markup=reply_markup,
            **extra_kwargs
        )
    elif mt == "video_note":
        if media is None:
            raise ValueError("video_note media is missing in payload")
        await bot.send_video_note(
            chat_id=chat_id,
            video_note=media,
            reply_markup=reply_markup,
            **extra_kwargs
        )
    else:
        await bot.send_message(
            chat_id=chat_id,
            text=caption or "",
            reply_markup=reply_markup,
            **extra_kwargs
        )


async def _maybe_await(result):
    if asyncio.iscoroutine(result):
        return await result
    return result


# ------------------ BroadcastManager ------------------
class BroadcastManager:
    """
    Minimal, robust broadcast manager for aiogram v3.
    Usage:
      manager = BroadcastManager(session_maker=AsyncSessionLocal, bot=bot, rate=20.0, concurrency=50)
      await manager.broadcast(payload=payload, admin_chat_id=ADMIN)
    """

    def __init__(
            self,
            session_maker: Callable[..., AsyncSession] = AsyncSessionLocal,
            bot=None,
            *,
            rate: float = 20.0,
            concurrency: int = 50,
            batch_size: int = 2000,
            queue_maxsize: int = 50_000,
            max_retries: int = 5,
            retryafter_cap: float = 300.0,
    ):
        self.session_maker = session_maker
        self.bot = bot
        self.rate_limiter = TokenBucket(rate=rate)
        self.concurrency = concurrency
        self.batch_size = batch_size
        self.queue_maxsize = queue_maxsize
        self.max_retries = max_retries
        self.retryafter_cap = float(retryafter_cap)
        self.logger = logger

    async def _mark_user_inactive(self, chat_id: int):
        # Prefer repo.mark_inactive, fallback to direct UPDATE
        try:
            if hasattr(repo, "mark_inactive"):
                async with self.session_maker() as s:
                    await repo.mark_inactive(s, chat_id)
                    try:
                        s.info["writes"] = True
                    except Exception:
                        pass
                    await s.commit()
                    return
        except Exception:
            self.logger.exception("repo.mark_inactive failed for %s, falling back", chat_id)

        try:
            async with self.session_maker() as s:
                await s.execute(update(User).where(User.chat_id == chat_id).values(is_active=False))
                try:
                    s.info["writes"] = True
                except Exception:
                    pass
                await s.commit()
                self.logger.info("Marked user %s inactive (fallback)", chat_id)
        except ProgrammingError as pe:
            self.logger.debug("Could not mark inactive (is_active absent?) for %s: %s", chat_id, pe)
        except Exception:
            self.logger.exception("Failed to mark user inactive for %s", chat_id)

    async def broadcast(
            self,
            payload: Dict[str, Any],
            admin_chat_id: int,
            *,
            dedupe: bool = True,
            external_stop_event: Optional[asyncio.Event] = None
    ) -> Dict[str, Any]:
        stats = {
            "total_enqueued": 0,
            "sent": 0,
            "failed": 0,
            "blocked": 0,
            "not_found": 0,
            "unauthorized": 0,
            "retry_after_count": 0,
            "start_ts": time.time(),
            "end_ts": None,
        }
        stats_lock = asyncio.Lock()
        q: asyncio.Queue = asyncio.Queue(maxsize=self.queue_maxsize)
        stop_event = external_stop_event or asyncio.Event()

        async def producer():
            try:
                async with self.session_maker() as session:
                    async for chat_id in iter_user_chat_ids(session, batch_size=self.batch_size):
                        # stop if signaled
                        if stop_event.is_set():
                            break
                        await q.put(chat_id)
                        async with stats_lock:
                            stats["total_enqueued"] += 1
                for _ in range(self.concurrency):
                    await q.put(None)
            except Exception as e:
                self.logger.exception("Producer failed: %s", e)
                for _ in range(self.concurrency):
                    await q.put(None)
                stop_event.set()

        async def _handle_permanent(chat_id: int, reason: str):
            self.logger.info("permanent failure for %s reason=%s", chat_id, reason)
            await self._mark_user_inactive(chat_id)

        async def send_to_chat(chat_id: int):
            attempt = 0
            backoff = 1.0
            while True:
                attempt += 1
                try:
                    await self.rate_limiter.consume(1.0)
                    await _send_via_bot(self.bot, chat_id, payload)
                    async with stats_lock:
                        stats["sent"] += 1
                    return True
                except RetryAfter as e:
                    raw_wait = getattr(e, "timeout", None) or getattr(e, "retry_after", None) or 5
                    wait_for = float(raw_wait)
                    if wait_for > self.retryafter_cap:
                        wait_for = self.retryafter_cap
                    async with stats_lock:
                        stats["retry_after_count"] += 1
                    if attempt >= self.max_retries:
                        async with stats_lock:
                            stats["failed"] += 1
                        await _handle_permanent(chat_id, "retry_after_too_many")
                        return False
                    self.logger.warning("RetryAfter for %s: sleeping %.1fs (attempt %s/%s)", chat_id, wait_for, attempt,
                                        self.max_retries)
                    await asyncio.sleep(wait_for + min(backoff, 10.0))
                    backoff = min(backoff * 2, 60.0)
                    continue
                except BotBlocked:
                    async with stats_lock:
                        stats["blocked"] += 1
                    self.logger.info("BotBlocked: %s", chat_id)
                    await _handle_permanent(chat_id, "bot_blocked")
                    return False
                except ChatNotFound:
                    async with stats_lock:
                        stats["not_found"] += 1
                    self.logger.info("ChatNotFound: %s", chat_id)
                    await _handle_permanent(chat_id, "chat_not_found")
                    return False
                except Unauthorized:
                    async with stats_lock:
                        stats["unauthorized"] += 1
                    self.logger.info("Unauthorized: %s", chat_id)
                    await _handle_permanent(chat_id, "unauthorized")
                    return False
                except TelegramAPIError as e:
                    self.logger.warning("TelegramAPIError for %s: %s (attempt %s/%s)", chat_id, e, attempt,
                                        self.max_retries)
                    if attempt >= self.max_retries:
                        async with stats_lock:
                            stats["failed"] += 1
                        await _handle_permanent(chat_id, "telegram_api_error_max_retries")
                        return False
                    await asyncio.sleep(backoff)
                    backoff = min(backoff * 2, 60.0)
                    continue
                except ValueError as e:
                    self.logger.exception("Payload error for %s: %s", chat_id, e)
                    async with stats_lock:
                        stats["failed"] += 1
                    await _handle_permanent(chat_id, "invalid_payload")
                    return False
                except Exception as e:
                    self.logger.exception("Unexpected send error for %s: %s", chat_id, e)
                    async with stats_lock:
                        stats["failed"] += 1
                    if attempt >= self.max_retries:
                        await _handle_permanent(chat_id, "unexpected_error")
                        return False
                    await asyncio.sleep(backoff)
                    backoff = min(backoff * 2, 60.0)
                    continue

        async def consumer_worker(worker_idx: int):
            while True:
                chat_id = await q.get()
                if chat_id is None:
                    q.task_done()
                    break
                if stop_event.is_set():
                    q.task_done()
                    break
                try:
                    await send_to_chat(chat_id)
                finally:
                    q.task_done()

        producer_task = asyncio.create_task(producer())
        consumers = [asyncio.create_task(consumer_worker(i)) for i in range(self.concurrency)]

        try:
            await producer_task
            await q.join()
            await asyncio.gather(*consumers, return_exceptions=True)
        finally:
            stats["end_ts"] = time.time()
            duration = stats["end_ts"] - stats["start_ts"]
            self.logger.info("Broadcast finished in %.2fs: stats=%s", duration, stats)
            await self._send_admin_report(admin_chat_id, payload, stats)
        return stats

    async def _send_admin_report(self, admin_chat_id: int, payload: Dict[str, Any], stats: Dict[str, Any]):
        total = stats.get("total_enqueued", 0)
        sent = stats.get("sent", 0)
        failed = stats.get("failed", 0)
        blocked = stats.get("blocked", 0)
        not_found = stats.get("not_found", 0)
        unauthorized = stats.get("unauthorized", 0)
        start = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(stats.get("start_ts", time.time())))
        end = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(stats.get("end_ts", time.time())))
        duration = stats.get("end_ts", time.time()) - stats.get("start_ts", time.time())

        msg = (
            "┏━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "┃  ✦  Broadcast report\n"
            "┣━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"┃ ✦ Type: {payload.get('media_type', 'text')}\n"
            f"┃ ✦ Total queued: {total}\n"
            f"┃ ✦ Sent: {sent}\n"
            f"┃ ✦ Failed: {failed}\n"
            f"┃ ✦ Blocked: {blocked}\n"
            f"┃ ✦ Not found: {not_found}\n"
            f"┃ ✦ Unauthorized: {unauthorized}\n"
            f"┃ ✦ Start: {start}\n"
            f"┃ ✦ End:   {end}\n"
            f"┃ ✦ Duration: {int(duration)}s\n"
            "┗━━━━━━━━━━━━━━━━━━━━━━━━"
        )
        try:
            await self.bot.send_message(chat_id=admin_chat_id, text=msg)
        except Exception:
            self.logger.exception("Failed to send admin report to %s", admin_chat_id)
