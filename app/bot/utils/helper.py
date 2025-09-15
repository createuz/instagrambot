import collections.abc
import typing

from aiogram import Dispatcher, types
from aiogram.fsm.storage.base import BaseEventIsolation, BaseStorage, DefaultKeyBuilder
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.fsm.strategy import FSMStrategy
from redis.asyncio.client import Redis

T = typing.TypeVar("T")


def chunks(list_to_split: typing.Sequence[T], chunk_size: int) -> collections.abc.Iterator[typing.Sequence[T]]:
    for i in range(0, len(list_to_split), chunk_size):
        yield list_to_split[i: i + chunk_size]


def get_redis_storage(redis: Redis):
    key_builder = DefaultKeyBuilder(with_bot_id=True)
    return RedisStorage(redis=redis, key_builder=key_builder)


def get_dispatcher(
        storage: BaseStorage = MemoryStorage(),
        fsm_strategy: FSMStrategy | None = FSMStrategy.CHAT,
        event_isolation: BaseEventIsolation | None = None,
):
    dp = Dispatcher(
        storage=storage,
        fsm_strategy=fsm_strategy,
        events_isolation=event_isolation,
    )
    return dp


MEDIA_TYPES = {
    types.ContentType.TEXT: 'text',
    types.ContentType.PHOTO: "photo",
    types.ContentType.VIDEO: "video",
    types.ContentType.AUDIO: "audio",
    types.ContentType.VOICE: "voice",
    types.ContentType.VIDEO_NOTE: "video_note",
    types.ContentType.ANIMATION: "animation",
}
