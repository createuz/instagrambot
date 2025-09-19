# app/monitoring/webserver.py
import asyncio
import time
from typing import Optional, Tuple

from aiohttp import web
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, REGISTRY

from app.core.logger import get_logger
from app.db.services.redis_manager import RedisManager
from app.db.sessions.session import AsyncSessionLocal

logger = get_logger()

DEFAULT_HOST = "127.0.0.1"  # recommended: bind to localhost in single-node deploy
DEFAULT_PORT = 8080
HEALTH_CHECK_TIMEOUT = 1.0  # seconds for external deps
HEALTH_CACHE_TTL = 5.0  # seconds - cache health results to reduce load


async def _check_db_once() -> bool:
    try:
        async with AsyncSessionLocal() as session:
            await session.execute("SELECT 1")
        return True
    except Exception:
        logger.debug("DB health check failed", exc_info=True)
        return False


async def _check_redis_once() -> bool:
    try:
        client = RedisManager.client()
        if client is None:
            return False
        return bool(await asyncio.wait_for(client.ping(), timeout=HEALTH_CHECK_TIMEOUT))
    except Exception:
        logger.debug("Redis health check failed", exc_info=True)
        return False


class WebServer:
    """
    Minimal aiohttp server exposing /healthz and /metrics.
    - Health checks are cached for HEALTH_CACHE_TTL seconds to avoid thundering DB/Redis.
    - Bind to 127.0.0.1 by default (recommended).
    """

    def __init__(self, host: str = DEFAULT_HOST, port: int = DEFAULT_PORT):
        self._host = host
        self._port = port
        self._runner: Optional[web.AppRunner] = None
        self._site: Optional[web.TCPSite] = None
        self._app: Optional[web.Application] = None
        self._last_health: Tuple[float, dict] = (0.0, {"status": "fail", "checks": {"db": False, "redis": False}})

    async def _compute_health(self) -> dict:
        # run checks concurrently and bounded by timeout
        try:
            db_task = asyncio.create_task(_check_db_once())
            redis_task = asyncio.create_task(_check_redis_once())
            done, _ = await asyncio.wait({db_task, redis_task}, timeout=HEALTH_CHECK_TIMEOUT)
            db_ok = db_task.result() if db_task in done else False
            redis_ok = redis_task.result() if redis_task in done else False
        except Exception:
            logger.exception("Health checks raised")
            db_ok = False
            redis_ok = False

        status = "ok" if (db_ok and redis_ok) else "fail"
        return {"status": status, "checks": {"db": db_ok, "redis": redis_ok}}

    async def _cached_health(self) -> dict:
        now = time.time()
        last_ts, last_val = self._last_health
        if now - last_ts <= HEALTH_CACHE_TTL:
            return last_val
        val = await self._compute_health()
        self._last_health = (now, val)
        return val

    async def health_handler(self, request: web.Request) -> web.Response:
        start = time.time()
        health = await self._cached_health()
        status_code = 200 if health["status"] == "ok" else 500

        # update gauges (best-effort)
        try:
            from app.monitoring.metrics import DB_UP, REDIS_UP, BOT_UP
            DB_UP.set(1 if health["checks"]["db"] else 0)
            REDIS_UP.set(1 if health["checks"]["redis"] else 0)
            BOT_UP.set(1 if health["status"] == "ok" else 0)
        except Exception:
            pass

        body = {
            "status": health["status"],
            "checks": health["checks"],
            "uptime_seconds": int(time.time() - request.app.get("started_at", time.time())),
            "timestamp": int(time.time()),
            "duration_ms": int((time.time() - start) * 1000),
        }
        return web.json_response(body, status=status_code)

    async def metrics_handler(self, request: web.Request) -> web.Response:
        data = generate_latest(REGISTRY)
        # set Content-Type header directly (avoid aiohttp charset error)
        return web.Response(body=data, headers={"Content-Type": CONTENT_TYPE_LATEST})

    async def root_handler(self, request: web.Request) -> web.Response:
        return web.Response(text="OK — monitoring endpoints: /healthz /metrics")

    async def start(self):
        if self._runner is not None:
            return
        self._app = web.Application()
        self._app["started_at"] = time.time()
        self._app.add_routes([
            web.get("/", self.root_handler),
            web.get("/healthz", self.health_handler),
            web.get("/metrics", self.metrics_handler),
        ])
        self._runner = web.AppRunner(self._app)
        await self._runner.setup()
        self._site = web.TCPSite(self._runner, self._host, self._port)
        await self._site.start()
        logger.info("monitor webserver started at http://%s:%d (health & metrics)", self._host, self._port)

    async def stop(self):
        if self._runner is None:
            return
        try:
            await self._runner.cleanup()
            logger.info("monitor webserver stopped")
        except Exception:
            logger.exception("monitor webserver stop failed")
        finally:
            self._runner = None
            self._site = None
            self._app = None
