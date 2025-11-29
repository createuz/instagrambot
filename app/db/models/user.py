from datetime import datetime
from typing import Optional

from sqlalchemy import String, DateTime, Integer, Boolean, BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from app.utils.custom_types import Int64
from .base import Base
from .dto import UserDto
from .mixins import TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[Optional[int]] = mapped_column(Integer, primary_key=True, autoincrement=True)
    chat_id: Mapped[Optional[Int64]] = mapped_column(BigInteger, unique=True, index=True, nullable=False)
    username: Mapped[Optional[str]] = mapped_column(String(length=64), nullable=True)
    first_name: Mapped[Optional[str]] = mapped_column(String(length=100), nullable=True)
    language: Mapped[Optional[str]] = mapped_column(String(length=2), nullable=True)
    language_code: Mapped[Optional[str]] = mapped_column(String(length=32), nullable=True)
    is_premium: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=False, default=False)
    ref_by: Mapped[Optional[str]] = mapped_column(String(length=32), nullable=True, default="bot")
    blocked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    def dto(self) -> UserDto:
        return UserDto.model_validate(self)
