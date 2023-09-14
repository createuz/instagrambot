from sqlalchemy import Column, String, Integer, func, BigInteger, Text
from sqlalchemy import update
from sqlalchemy.future import select
from databasedb import Base, db
from sqlalchemy import delete
from sqlalchemy import JSON

db.init()


class User(Base):
    __tablename__ = "users"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    chat_id = Column(BigInteger, unique=True)
    username = Column(String)
    first_name = Column(String)
    language = Column(String)

    @classmethod
    async def create_user(cls, chat_id, username, first_name, language):
        user = cls(chat_id=chat_id, username=username, first_name=first_name, language=language)
        async with db() as session:
            session.add(user)
            try:
                await session.commit()
            except Exception:
                await session.rollback()
                raise
        return user

    @classmethod
    async def update_language(cls, chat_id, new_language):
        async with db() as session:
            await session.execute(update(cls).where(cls.chat_id == chat_id).values(language=new_language))
            try:
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    @classmethod
    async def get_language(cls, chat_id):
        async with db() as session:
            return await session.scalar(select(cls.language).where(cls.chat_id == chat_id))

    @classmethod
    async def get_all_user(cls, admin_language):
        async with db() as session:
            query = select(cls.chat_id)
            if admin_language == 'Uzbek':
                query = query.where(cls.language == admin_language)
            result = await session.execute(query.where(cls.language != admin_language))
            return [row[0] for row in result.all()]

    @classmethod
    async def count_users(cls):
        async with db() as session:
            return await session.scalar(select(func.count(cls.chat_id)))


class Group(Base):
    __tablename__ = "groups"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    chat_id = Column(BigInteger, nullable=True, unique=True)
    group_name = Column(String)
    group_username = Column(String)
    group_type = Column(String)
    group_members = Column(BigInteger)
    language = Column(String)

    @classmethod
    async def create_group(cls, chat_id, group_name, group_username, group_members, language):
        group = cls(chat_id=chat_id, group_name=group_name, group_username=group_username,
                    group_members=group_members, language=language)
        async with db() as session:
            session.add(group)
            try:
                await session.commit()
            except Exception:
                await session.rollback()
                raise
        return group

    @classmethod
    async def update_language(cls, chat_id, new_language):
        async with db() as session:
            await session.execute(update(cls).where(cls.chat_id == chat_id).values(language=new_language))
            try:
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    @classmethod
    async def get_language(cls, chat_id):
        async with db() as session:
            return await session.scalar(select(cls.language).where(cls.chat_id == chat_id))

    @classmethod
    async def get_all_group(cls, admin_language):
        async with db() as session:
            query = select(cls.chat_id)
            if admin_language == 'Uzbek':
                query = query.where(cls.language == admin_language)
            result = await session.execute(query.where(cls.language != admin_language))
            return [row[0] for row in result.all()]

    @classmethod
    async def count_group(cls):
        async with db() as session:
            return await session.scalar(select(func.count(cls.chat_id)))


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
    async def update_chat_id(cls, chat_id, **kwargs):
        async with db() as session:
            await session.execute(update(cls).where(cls.chat_id == chat_id).values(**kwargs))
            try:
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    @classmethod
    async def get_chat_id(cls, chat_id):
        async with db() as session:
            return await session.scalar(select(cls.chat_id).where(cls.chat_id == chat_id))

    @classmethod
    async def get_all_admin(cls):
        async with db() as session:
            result = await session.execute(select(cls.chat_id))
            return [row[0] for row in result.all()]

    @classmethod
    async def delete(cls, chat_id):
        query = delete(cls).where(cls.chat_id == chat_id)

        async with db() as session:
            await session.execute(query)
            try:
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            return True

    @classmethod
    async def count_admin(cls):
        async with db() as session:
            return await session.scalar(select(func.count(cls.chat_id)))


class Channel(Base):
    __tablename__ = 'channels'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    chat_id = Column(BigInteger, unique=True)
    title = Column(String)
    username = Column(String)
    invite_link = Column(String, unique=True)

    @classmethod
    async def create_channel(cls, chat_id, title, username, invite_link):
        channel = cls(chat_id=chat_id, title=title, username=username, invite_link=invite_link)
        async with db() as session:
            session.add(channel)
            try:
                await session.commit()
            except Exception:
                await session.rollback()
                raise
        return channel

    @classmethod
    async def update(cls, chat_id, **kwargs):
        async with db() as session:
            await session.execute(update(cls).where(cls.chat_id == chat_id).values(**kwargs))
            try:
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    @classmethod
    async def get_chat_id(cls, chat_id):
        async with db() as session:
            return await session.scalar(select(cls.chat_id).where(cls.chat_id == chat_id))

    @classmethod
    async def get_all_channel(cls):
        async with db() as session:
            result = await session.execute(select(cls.chat_id))
            return [row[0] for row in result.all()]

    @classmethod
    async def delete(cls, chat_id):
        query = delete(cls).where(cls.chat_id == chat_id)
        async with db() as session:
            await session.execute(query)
            try:
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            return True

    @classmethod
    async def count_channel(cls):
        async with db() as session:
            return await session.scalar(select(func.count(cls.chat_id)))


class InstagramMediaDB(Base):
    __tablename__ = 'media'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    video_id = Column(Text)
    video_url = Column(JSON)

    @classmethod
    async def create_media_list(cls, video_id, video_url):
        media = cls(video_id=video_id, video_url=video_url)
        async with db() as session:
            session.add(media)
            try:
                await session.commit()
            except Exception:
                await session.rollback()
                raise
        return media

    @classmethod
    async def get_video_url(cls, video_id):
        async with db() as session:
            return await session.scalar(select(cls.video_url).where(cls.video_id == video_id))

    @classmethod
    async def get_all_video_url(cls):
        async with db() as session:
            result = await session.execute(select(cls.video_url))
            return [row[0] for row in result.all()]

    @classmethod
    async def delete(cls, video_id):
        async with db() as session:
            await session.execute(delete(cls).where(cls.video_id == video_id))
            try:
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            return True
