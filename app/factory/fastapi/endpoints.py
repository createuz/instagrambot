# app/api/endpoints.py
import asyncio
from typing import Optional

from fastapi import APIRouter, Request, Response

from app.factory.fastapi.healthcheck import HealthResponse, HealthChecker
from app.utils.time import get_uptime

router = APIRouter(prefix="/health")


@router.get("/liveness", response_model=HealthResponse)
async def liveness() -> HealthResponse:
    uptime = get_uptime()
    return HealthResponse(
        uptime=uptime,
        ok=True,
        results=[{"name": "service", "ok": True, "message": "alive"}],
    )


@router.get("/readiness", response_model=HealthResponse)
async def readiness(
    request: Request, response: Response, timeout: Optional[float] = 2.0
) -> HealthResponse:
    bot = getattr(request.app.state, "bot", None)
    dispatcher = getattr(request.app.state, "dispatcher", None)
    redis_repo = getattr(request.app.state, "redis_repository", None)
    db_engine = getattr(request.app.state, "db_engine", None)
    checker = HealthChecker(
        bot=bot, dispatcher=dispatcher, redis_repo=redis_repo, db_engine=db_engine
    )
    try:
        resp: HealthResponse = await asyncio.wait_for(
            checker.run_checks(), timeout=timeout
        )
    except asyncio.TimeoutError:
        uptime = get_uptime()
        resp = HealthResponse(
            uptime=uptime,
            ok=False,
            results=[{"name": "overall", "ok": False, "message": "timeout"}],
        )
    response.status_code = resp.status_code()
    return resp
