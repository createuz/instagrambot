from datetime import datetime
from typing import Optional

from aiogram import html
from aiogram.utils.link import create_tg_link

from app.db.base import ActiveRecordModel
from app.utils.custom_types import Int64


class UserDto(ActiveRecordModel):
    id: int
    chat_id: Optional[Int64]
    username: Optional[str]
    first_name: Optional[str]
    language: Optional[str]
    language_code: Optional[str]
    is_premium: Optional[bool]
    ref_by: Optional[str]
    blocked_at: Optional[datetime]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    @property
    def url(self) -> str:
        return create_tg_link("user", id=self.chat_id)

    @property
    def mention(self) -> str:
        return html.link(value=self.first_name, link=self.url)
