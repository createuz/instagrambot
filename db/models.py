from datetime import datetime, timedelta
from sqlalchemy import Column, String, Integer, func, BigInteger, update, delete, DateTime, and_
from sqlalchemy.future import select
from db.database import Base, db

db.init()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(BigInteger, unique=True, index=True)
    username = Column(String)
    first_name = Column(String)
    language = Column(String)
    added_by = Column(String)
    created_add = Column(DateTime)

    @classmethod
    async def create_user(cls, chat_id: int, username: str, first_name: str, language: str, added_by: str):
        user = cls(chat_id=chat_id, username=username,
                   first_name=first_name, language=language, added_by=added_by, created_add=datetime.now())
        async with db() as session:
            session.add(user)
            try:
                await session.commit()
            except Exception:
                await session.rollback()
                raise
        return user

    @classmethod
    async def update_language(cls, chat_id: int, language: str):
        async with db() as session:
            await session.execute(update(cls).where(cls.chat_id == chat_id).values(language=language))
            try:
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    @classmethod
    async def get_language(cls, chat_id: int):
        async with db() as session:
            return await session.scalar(select(cls.language).where(cls.chat_id == chat_id))

    @classmethod
    async def get_user_data(cls, chat_id: int):
        async with db() as session:
            user = await session.scalar(select(cls).where(cls.chat_id == chat_id))
            if user:
                return user.chat_id, user.username, user.first_name
        return None, None, None

    @classmethod
    async def get_all_users(cls, admin_lang: str):
        query = (cls.language == admin_lang) if admin_lang == 'Uzbek' else (cls.language != 'Uzbek')
        async with db() as session:
            result = await session.execute(select(cls.chat_id).where(query))
            return [row[0] for row in result.all()]

    @classmethod
    async def get_all_chat_ids(cls):
        async with db() as session:
            result = await session.execute(select(cls.chat_id))
            return [row[0] for row in result.all()]

    @classmethod
    async def joined_last_month(cls):
        last_month = datetime.now() - timedelta(days=30)
        async with db() as session:
            return await session.scalar(select(func.count(cls.chat_id)).where(cls.created_add >= last_month))

    @classmethod
    async def joined_last_24_hours(cls):
        last_24_hours = datetime.now() - timedelta(hours=24)
        async with db() as session:
            return await session.scalar(select(func.count(cls.chat_id)).where(
                and_(cls.created_add >= last_24_hours, cls.created_add <= datetime.now())))


class Group(Base):
    __tablename__ = "groups"
    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(BigInteger, unique=True, index=True)
    name = Column(String)
    username = Column(String)
    members = Column(Integer)
    language = Column(String)
    created_add = Column(DateTime, default=datetime.now())

    @classmethod
    async def create_group(cls, chat_id: int, name: str, username: str, members: int, language: str):
        group = cls(chat_id=chat_id, name=name, username=username, members=members, language=language)
        async with db() as session:
            session.add(group)
            try:
                await session.commit()
            except Exception:
                await session.rollback()
                raise
        return group

    @classmethod
    async def update_language(cls, chat_id: int, language: str):
        async with db() as session:
            await session.execute(update(cls).where(cls.chat_id == chat_id).values(language=language))
            try:
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    @classmethod
    async def get_language(cls, chat_id: int):
        async with db() as session:
            return await session.scalar(select(cls.language).where(cls.chat_id == chat_id))

    @classmethod
    async def get_all_groups(cls, admin_lang: str):
        query = (cls.language == admin_lang) if admin_lang == 'Uzbek' else (cls.language != 'Uzbek')
        async with db() as session:
            result = await session.execute(select(cls.chat_id).where(query))
            return [row[0] for row in result.all()]

    @classmethod
    async def get_all_chat_ids(cls):
        async with db() as session:
            result = await session.execute(select(cls.chat_id))
            return [row[0] for row in result.all()]

    @classmethod
    async def joined_last_month(cls):
        last_month = datetime.now() - timedelta(days=30)
        async with db() as session:
            return await session.scalar(select(func.count(cls.chat_id)).where(cls.created_add >= last_month))

    @classmethod
    async def joined_last_24_hours(cls):
        last_24_hours = datetime.now() - timedelta(hours=24)
        async with db() as session:
            return await session.scalar(select(func.count(cls.chat_id)).where(
                and_(cls.created_add >= last_24_hours, cls.created_add <= datetime.now())))


class Admin(Base):
    __tablename__ = 'admins'
    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(BigInteger, unique=True)
    username = Column(String)
    first_name = Column(String)

    @classmethod
    async def create_admin(cls, chat_id, username, first_name):
        admin = cls(chat_id=chat_id, username=username, first_name=first_name)
        async with db() as session:
            session.add(admin)
            try:
                await session.commit()
            except Exception:
                await session.rollback()
                raise
        return admin

    @classmethod
    async def get_admins_data(cls):
        async with db() as session:
            users = await session.execute(select(cls.chat_id, cls.first_name))
            if users:
                return [user for user in users]
        return None

    @classmethod
    async def get_all_admin(cls):
        async with db() as session:
            result = await session.execute(select(cls.chat_id))
            return [row[0] for row in result.all()]

    @classmethod
    async def delete_admin(cls, chat_id):
        query = delete(cls).where(cls.chat_id == int(chat_id))
        async with db() as session:
            await session.execute(query)
            try:
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            return True
