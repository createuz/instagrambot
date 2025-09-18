# app/core/logger.py
import logging
import sys
from collections import OrderedDict
from typing import MutableMapping

import orjson
import structlog

from app.core.config import conf  # sizning conf obyekt


def orjson_dumps(v, *, default=None):
    return orjson.dumps(v, default=default).decode()


def _reorder_event_keys(_, __, event_dict: MutableMapping) -> MutableMapping:
    od = OrderedDict()
    event_val = event_dict.pop("event", None)
    if event_val is not None:
        od["event"] = event_val
    for k, v in event_dict.items():
        od[k] = v
    return od


def setup_logger():
    level_name = (getattr(conf, "bot", None) and getattr(conf.bot, "log_level", None)) or "INFO"
    level = getattr(logging, level_name.upper(), logging.INFO)

    root = logging.getLogger()
    for h in list(root.handlers):
        root.removeHandler(h)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter("%(message)s"))
    root.addHandler(handler)
    root.setLevel(level)

    processors = [
        structlog.processors.TimeStamper(fmt="iso", utc=True),  # adds "timestamp"
        structlog.processors.add_log_level,  # adds "level"
        _reorder_event_keys,  # reorder keys and return OrderedDict
        structlog.processors.JSONRenderer(serializer=orjson_dumps),
    ]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(level),
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

    for name in ("aiogram", "aiogram.dispatcher", "aiogram.client", "aiohttp", "asyncio"):
        lg = logging.getLogger(name)
        lg.setLevel(logging.WARNING)
        lg.propagate = True

    return structlog.get_logger()


_logger = setup_logger()


def get_logger():
    return _logger
