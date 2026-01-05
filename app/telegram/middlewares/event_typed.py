from abc import ABC
from typing import ClassVar, Final, Any, List, Iterable

from aiogram import BaseMiddleware, Router

from app.utils.enums import MiddlewareEventType

DEFAULT_UPDATE_TYPES: Final[list[MiddlewareEventType]] = [
    MiddlewareEventType.MESSAGE,
    MiddlewareEventType.CALLBACK_QUERY,
    MiddlewareEventType.MY_CHAT_MEMBER,
    MiddlewareEventType.ERROR,
    MiddlewareEventType.INLINE_QUERY,
]


class EventTypedMiddleware(BaseMiddleware, ABC):
    __event_types__: ClassVar[List[Any]] = []

    def _normalize_event_type(self, ev: Any) -> str:
        if hasattr(ev, "value"):
            return str(ev.value)
        return str(ev)

    def get_event_types(self, router: Router) -> List[str]:
        types: Iterable[Any] = self.__event_types__ or router.resolve_used_update_types()
        return [self._normalize_event_type(t) for t in types]

    def setup_inner(self, router: Router) -> None:
        for event_type in self.get_event_types(router=router):
            observer = router.observers.get(event_type)
            if observer:
                observer.middleware(self)

    def setup_outer(self, router: Router) -> None:
        for event_type in self.get_event_types(router=router):
            observer = router.observers.get(event_type)
            if observer:
                observer.outer_middleware(self)
