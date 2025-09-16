# app/db/user_repo.py
from datetime import datetime, timedelta
from typing import Optional, List, Tuple

from sqlalchemy import select, func, and_, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logger import get_logger
from app.db.models.user import User


class UserRepo:
    def __init__(self, logger=None):
        self.logger = logger or get_logger()

    @staticmethod
    def _mark_writes(session: AsyncSession) -> None:
        try:
            session.info["writes"] = True
        except Exception:
            pass

    async def mark_inactive(self, session: AsyncSession, chat_id: int) -> None:
        try:
            await session.execute(update(User).where(User.chat_id == chat_id).values(is_active=False))
            self._mark_writes(session)
            self.logger.info("mark_inactive: chat_id=%s", chat_id)
        except Exception:
            self.logger.exception("mark_inactive failed for chat_id=%s", chat_id)
            raise

    async def ensure_user(self,
                          session: AsyncSession,
                          chat_id: int,
                          username: Optional[str] = None,
                          first_name: Optional[str] = None,
                          is_premium: Optional[bool] = None,
                          default_lang: Optional[str] = None,
                          added_by: Optional[str] = None) -> int:
        try:
            ins = pg_insert(User).values(
                chat_id=chat_id,
                username=username,
                first_name=first_name,
                is_premium=is_premium,
                language=default_lang,
                added_by=added_by
            )

            stmt = ins.on_conflict_do_update(
                index_elements=[User.chat_id],
                set_={
                    "username": ins.excluded.username,
                    "first_name": ins.excluded.first_name,
                    "is_premium": ins.excluded.is_premium,
                }
            ).returning(User.id)

            res = await session.execute(stmt)
            self._mark_writes(session)
            user_id = res.scalar_one()
            self.logger.info("ensure_user: upsert chat_id=%s id=%s", chat_id, user_id)
            return user_id
        except SQLAlchemyError as e:
            self.logger.exception("ensure_user failed for %s: %s", chat_id, e)
            raise

    async def upsert_language(self, session: AsyncSession, chat_id: int, language: str) -> int:
        try:
            ins = pg_insert(User).values(chat_id=chat_id, language=language)
            stmt = ins.on_conflict_do_update(
                index_elements=[User.chat_id],
                set_={"language": ins.excluded.language}
            ).returning(User.id)

            res = await session.execute(stmt)
            self._mark_writes(session)
            user_id = res.scalar_one()
            self.logger.info("upsert_language: chat_id=%s id=%s lang=%s", chat_id, user_id, language)
            return user_id

        except SQLAlchemyError as e:
            self.logger.exception("upsert_language failed for %s: %s", chat_id, e)
            raise

    @staticmethod
    async def get_user(session: AsyncSession, chat_id: int) -> Optional[User]:
        res = await session.execute(select(User).where(User.chat_id == chat_id).limit(1))
        return res.scalars().first()

    @staticmethod
    async def get_language(session: AsyncSession, chat_id: int) -> Optional[str]:
        res = await session.execute(select(User.language).where(User.chat_id == chat_id).limit(1))
        return res.scalar_one_or_none()

    async def get_basic(self, session: AsyncSession, chat_id: int) -> Tuple[
        Optional[int], Optional[str], Optional[str]]:
        u = await self.get_user(session, chat_id)
        if u:
            return u.chat_id, u.username, u.first_name
        return None, None, None

    @staticmethod
    async def get_all_user_ids(session: AsyncSession) -> List[int]:
        res = await session.execute(select(User.chat_id))
        return list(res.scalars())

    @staticmethod
    async def get_all_users(session: AsyncSession):
        res = await session.execute(
            select(
                User.chat_id,
                User.username,
                User.first_name,
                User.language,
                User.is_premium,
                User.added_by,
                User.created_at
            )
        )
        rows = res.all()
        return [
            {
                "chat_id": r.chat_id,
                "username": r.username,
                "first_name": r.first_name,
                "language": r.language,
                "is_premium": r.is_premium,
                "added_by": r.added_by,
                "created_at": str(r.created_at)
            } for r in rows
        ]

    @staticmethod
    async def joined_last_month(session: AsyncSession) -> int:
        cutoff = datetime.utcnow() - timedelta(days=30)
        res = await session.execute(select(func.count(User.chat_id)).where(User.created_at >= cutoff))
        return res.scalar_one_or_none() or 0

    @staticmethod
    async def joined_last_24h(session: AsyncSession) -> int:
        cutoff = datetime.utcnow() - timedelta(hours=24)
        now = datetime.utcnow()
        res = await session.execute(select(func.count(User.chat_id)).where(
            and_(User.created_at >= cutoff, User.created_at <= now)
        ))
        return res.scalar_one_or_none() or 0
