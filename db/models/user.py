from datetime import datetime, timezone, timedelta
from typing import Optional, List

from sqlalchemy import Integer, String, BigInteger, DateTime, func, update, and_, Boolean
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import mapped_column, Mapped

from db.database import db, cache, Base


def utc_now():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    chat_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True, nullable=False)
    username: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    first_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    is_premium: Mapped[bool] = mapped_column(Boolean, nullable=True)
    language: Mapped[str] = mapped_column(String, nullable=False)
    added_by: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)

    @classmethod
    async def create_user(
            cls,
            session: AsyncSession,
            chat_id: int,
            username: Optional[str],
            first_name: Optional[str],
            is_premium: Optional[bool],
            language: str,
            added_by: Optional[str]
    ) -> "User":
        try:
            user = cls(
                chat_id=chat_id,
                username=username,
                first_name=first_name,
                is_premium=is_premium,
                language=language,
                added_by=added_by,
            )
            session.add(user)
            await cls.commit_session(session)
            return user
        except SQLAlchemyError as e:
            await session.rollback()
            raise RuntimeError(f"Error creating user: {e}")

    @staticmethod
    async def commit_session(session: AsyncSession):
        try:
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise RuntimeError(f"Database operation failed: {e}")

    @classmethod
    async def get_language(cls, chat_id: int) -> Optional[str]:
        async with db.get_session() as session:
            return await session.scalar(select(cls.language).where(cls.chat_id == chat_id))

    @classmethod
    async def update_language(cls, chat_id: int, language: str):
        async with db.get_session() as session:
            await session.execute(update(cls).where(cls.chat_id == chat_id).values(language=language))
            await cls.commit_session(session)
            cache_key = f"get_language_{chat_id}"
            await cache.delete(cache_key)
            await cache.set(cache_key, language, 3600)

    @classmethod
    async def get_user(cls, chat_id: int) -> Optional[tuple]:
        async with db.get_session() as session:
            user = await session.scalar(select(cls).where(cls.chat_id == chat_id))
            if user:
                return user.chat_id, user.username, user.first_name
            return None, None, None

    @classmethod
    async def get_users(cls, session: AsyncSession, chat_id: int) -> Optional["User"]:
        try:
            stmt = select(cls).where(cls.chat_id == chat_id)
            user: Optional[User] = (await session.execute(stmt)).scalar_one_or_none()
            return user
        except SQLAlchemyError as e:
            raise RuntimeError(f"Error retrieving user: {e}")

    @classmethod
    async def get_all_userss(cls, admin_lang: Optional[str] = None) -> List[int]:
        async with db.get_session() as session:
            query = select(cls.chat_id)
            if admin_lang:
                query = query.where(cls.language == ('Uzbek' if admin_lang == 'Uzbek' else cls.language != 'Uzbek'))
            result = await session.execute(query)
            return [row for row in result.scalars()]

    @classmethod
    async def get_all_users(cls, admin_lang: Optional[str] = None):
        async with db.get_session() as session:
            if admin_lang is None:
                query = select(cls.chat_id, cls.username, cls.first_name, cls.language, cls.is_premium, cls.added_by,
                               cls.created_at)
                result = await session.execute(query)
                return [
                    {
                        "chat_id": user.chat_id,
                        "username": user.username,
                        "first_name": user.first_name,
                        "language": user.language,
                        'is_premium': user.is_premium,
                        "added_by": user.added_by,
                        "created_at": f"{user.created_at}"
                    } for user in result.all()
                ]
            else:
                query = cls.language == admin_lang if admin_lang == 'Uzbek' else 'Uzbek' != cls.language
                result = await session.execute(select(cls.chat_id).where(query))
                return [chat_id for chat_id in result.all()]

    @classmethod
    async def joined_last_month(cls) -> Optional[int]:
        last_month = datetime.now() - timedelta(days=30)
        async with db.get_session() as session:
            return await session.scalar(select(func.count(cls.chat_id)).where(cls.created_at >= last_month))

    @classmethod
    async def joined_last_24_hours(cls) -> Optional[int]:
        last_24_hours = datetime.now() - timedelta(hours=24)
        async with db.get_session() as session:
            return await session.scalar(select(func.count(cls.chat_id)).where(
                and_(cls.created_at >= last_24_hours, cls.created_at <= datetime.now())))
