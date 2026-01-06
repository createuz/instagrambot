# app/factory/fastapi/healthcheck.py
from __future__ import annotations

import asyncio
from typing import Any, Optional, List

from aiogram import Bot, Dispatcher
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from app.db.postgres import SQLSessionContext
from app.utils.time import get_uptime


class CheckerResult(BaseModel):
    name: str
    ok: bool
    message: str


class HealthResponse(BaseModel):
    uptime: int = Field(default_factory=get_uptime)  # seconds
    ok: bool = Field(default=True)
    results: List[CheckerResult] = Field(default_factory=list)

    def finalize(self) -> None:
        self.ok = all(r.ok for r in self.results)

    def status_code(self) -> int:
        self.finalize()
        return 200 if self.ok else 503


TELEGRAM_TIMEOUT = 0.6
REDIS_TIMEOUT = 0.5
POSTGRES_TIMEOUT = 0.7
DISPATCHER_TIMEOUT = 0.15


class HealthChecker:
    def __init__(
            self,
            *,
            bot: Optional[Bot] = None,
            dispatcher: Optional[Dispatcher] = None,
            redis_repo: Optional[Any] = None,
            session_pool: Optional[async_sessionmaker[AsyncSession]] = None
    ):
        self.bot = bot
        self.dispatcher = dispatcher
        self.redis = redis_repo
        self.session_pool = session_pool

    async def _check_telegram(self) -> CheckerResult:
        if not self.bot:
            return CheckerResult(name="bot", ok=False, message="bot not provided")
        try:
            me = await asyncio.wait_for(self.bot.get_me(), timeout=TELEGRAM_TIMEOUT)
            username = getattr(me, "username", None) or getattr(me, "first_name", "ok")
            return CheckerResult(name="bot", ok=True, message=str(username))
        except asyncio.TimeoutError:
            return CheckerResult(name="bot", ok=False, message="timeout")
        except Exception as e:
            return CheckerResult(name="bot", ok=False, message=str(e))

    async def _check_redis(self) -> CheckerResult:
        if not self.redis:
            return CheckerResult(name="cache", ok=False, message="not configured")
        try:
            pong = await asyncio.wait_for(self.redis.client.ping(), timeout=REDIS_TIMEOUT)
            return CheckerResult(name="cache", ok=True, message=str(pong))
        except asyncio.TimeoutError:
            return CheckerResult(name="cache", ok=False, message="timeout")
        except Exception as e:
            return CheckerResult(name="cache", ok=False, message=str(e))

    async def _check_postgres(self) -> CheckerResult:
        if not self.session_pool:
            return CheckerResult(name="postgres", ok=False, message="not configured")
        try:
            async with SQLSessionContext(session_pool=self.session_pool) as (repository, uow):
                await asyncio.wait_for(uow.execute(text("SELECT 1")), timeout=POSTGRES_TIMEOUT)
            return CheckerResult(name="postgres", ok=True, message="ok")
        except asyncio.TimeoutError:
            return CheckerResult(name="postgres", ok=False, message="timeout")
        except Exception as e:
            return CheckerResult(name="postgres", ok=False, message=str(e))

    async def _check_dispatcher(self) -> CheckerResult:
        try:
            if self.dispatcher is not None:
                if hasattr(self.dispatcher, "is_running"):
                    running = bool(getattr(self.dispatcher, "is_running"))
                else:
                    lock = getattr(self.dispatcher, "_running_lock", None)
                    running = bool(lock and lock.locked())
                return CheckerResult(
                    name="dispatcher",
                    ok=running,
                    message="polling" if running else "not running",
                )
            if self.bot is not None:
                try:
                    info = await asyncio.wait_for(
                        self.bot.get_webhook_info(), timeout=DISPATCHER_TIMEOUT
                    )
                    url = getattr(info, "url", None)
                    ok = bool(url)
                    return CheckerResult(
                        name="dispatcher",
                        ok=ok,
                        message="webhook" if ok else "no webhook",
                    )
                except asyncio.TimeoutError:
                    return CheckerResult(
                        name="dispatcher", ok=False, message="webhook timeout"
                    )
                except Exception as e:
                    return CheckerResult(name="dispatcher", ok=False, message=str(e))
            return CheckerResult(
                name="dispatcher", ok=False, message="no dispatcher/bot provided"
            )
        except Exception as e:
            return CheckerResult(name="dispatcher", ok=False, message=str(e))

    async def run_checks(
            self, *, include: Optional[List[str]] = None, uptime: Optional[int] = None
    ) -> HealthResponse:
        if uptime is None:
            uptime = get_uptime()
        resp = HealthResponse(uptime=int(uptime or 0), ok=True, results=[])
        tasks = {}
        if include is None or "bot" in include:
            tasks["bot"] = asyncio.create_task(self._check_telegram())
        if include is None or "cache" in include:
            tasks["cache"] = asyncio.create_task(self._check_redis())
        if include is None or "postgres" in include:
            tasks["postgres"] = asyncio.create_task(self._check_postgres())
        if include is None or "dispatcher" in include:
            tasks["dispatcher"] = asyncio.create_task(self._check_dispatcher())
        if not tasks:
            resp.results.append(
                CheckerResult(name="service", ok=True, message="no checks")
            )
            resp.finalize()
            return resp

        done = await asyncio.gather(*tasks.values(), return_exceptions=True)
        for name, result in zip(tasks.keys(), done):
            if isinstance(result, CheckerResult):
                resp.results.append(result)
            else:
                resp.results.append(
                    CheckerResult(name=name, ok=False, message=str(result))
                )
        resp.finalize()
        return resp
