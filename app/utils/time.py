# app/utils/time.py
from __future__ import annotations

import time
from datetime import datetime

from app.utils.const import TIMEZONE

START_TIME: float = time.time()
START_MONOTONIC_TIME: float = time.monotonic()


def datetime_now() -> datetime:
    return datetime.now(tz=TIMEZONE)


def set_start_time() -> None:
    global START_TIME, START_MONOTONIC_TIME
    START_TIME = time.time()
    START_MONOTONIC_TIME = time.monotonic()


def get_uptime() -> int:
    return int(time.monotonic() - START_MONOTONIC_TIME)


def get_start_time() -> str:
    return datetime.fromtimestamp(START_TIME, tz=TIMEZONE).isoformat()
