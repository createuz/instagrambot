import asyncio
from datetime import datetime, timedelta
from sqlalchemy import Column, String, Integer, func, BigInteger, Text, update, delete, JSON, DateTime, and_
from sqlalchemy.future import select
from utlis.database import Base, db

db.init()
all_users_d = [
    {'chat_id': 6140152652, 'username': 'vknavo', 'first_name': 'cybernic', 'language': 'Uzbek',
     'created_add': '2023-12-22 22:55:30.445416'},
    {'chat_id': 2122060851, 'username': 'Lisi_foster', 'first_name': 'FELIX💞', 'language': 'Russian',
     'created_add': '2023-12-22 22:55:30.445416'},
    {'chat_id': 659538138, 'username': 'ksucherryy', 'first_name': 'кsu', 'language': 'Russian',
     'created_add': '2023-12-22 22:55:30.445416'},
    {'chat_id': 5247384230, 'username': None, 'first_name': 'Наталья', 'language': 'Russian',
     'created_add': '2023-12-22 22:55:30.445416'},
    {'chat_id': 5322118829, 'username': 'fekelavs', 'first_name': '😈', 'language': 'Russian',
     'created_add': '2023-12-22 22:55:30.445416'},
    {'chat_id': 5685563198, 'username': 'nuriddin_dev', 'first_name': 'Nuriddin', 'language': 'Uzbek',
     'created_add': '2023-12-22 22:55:30.445416'},
    {'chat_id': 5496078819, 'username': 'nani6841', 'first_name': 'nani6841_', 'language': 'Uzbek',
     'created_add': '2023-12-22 22:55:30.445416'},
    {'chat_id': 5467137967, 'username': None, 'first_name': '.', 'language': 'Russian',
     'created_add': '2023-12-22 22:55:30.445416'},
    {'chat_id': 5562771039, 'username': 'sales_manager_JM', 'first_name': '🟣Яна', 'language': 'Russian',
     'created_add': '2023-12-22 22:55:30.445416'},
    {'chat_id': 114254341, 'username': 'leesilverberg', 'first_name': 'Lee', 'language': None,
     'created_add': '2023-12-22 22:55:30.445416'},
    {'chat_id': 1359466461, 'username': 'Azimjon1828', 'first_name': 'Azim | Designs', 'language': 'Uzbek',
     'created_add': '2023-12-22 22:55:30.445416'},
    {'chat_id': 6581732107, 'username': None, 'first_name': 'Shavkat', 'language': 'Uzbek',
     'created_add': '2023-12-22 22:55:30.445416'},
    {'chat_id': 1999061722, 'username': 'jurayev_dev', 'first_name': 'Жўраев Фирдавс ₪ | Океан', 'language': 'Uzbek',
     'created_add': '2023-12-22 22:55:30.445416'},
    {'chat_id': 378569270, 'username': 'KoderNet', 'first_name': 'ҡσ∂ε૨ɳεт', 'language': 'Uzbek',
     'created_add': '2023-12-22 22:55:30.445416'},
    {'chat_id': 562082781, 'username': 'ZioZeo', 'first_name': 'ZioZeo', 'language': 'Russian',
     'created_add': '2023-12-22 22:55:30.445416'},
    {'chat_id': 648193464, 'username': 'Shefaahijazy', 'first_name': 'Shefaa', 'language': 'Arabic',
     'created_add': '2023-12-22 22:55:30.445416'},
    {'chat_id': 6058765315, 'username': 'fuckincrazy1', 'first_name': 'comet', 'language': 'English',
     'created_add': '2023-12-22 22:55:30.445416'},
    {'chat_id': 1916165356, 'username': 'Per_so_nali_ty', 'first_name': '🐊𝖁𝖑𝖆𝖉𝖑𝖊𝖓𝖆🐊', 'language': 'Russian',
     'created_add': '2023-12-22 22:55:30.445416'},
    {'chat_id': 5193461306, 'username': 'Vik_usichka', 'first_name': 'Викуся', 'language': 'Ukraine',
     'created_add': '2023-12-22 22:55:30.445416'},
    {'chat_id': 337124266, 'username': 'RodrigezGarsea', 'first_name': 'Rodgeras', 'language': 'Russian',
     'created_add': '2023-12-22 22:55:30.445416'},
    {'chat_id': 6336480158, 'username': 'asd_bruhh', 'first_name': 'Asd', 'language': 'Uzbek',
     'created_add': '2023-12-22 22:55:30.445416'},
    {'chat_id': 6318747772, 'username': None, 'first_name': 'Худойназаров Эргаш', 'language': 'Uzbek',
     'created_add': '2023-12-22 22:55:30.445416'},
    {'chat_id': 5721688828, 'username': None, 'first_name': '….', 'language': 'Russian',
     'created_add': '2023-12-22 22:55:30.445416'},
    {'chat_id': 2122911944, 'username': 'smile_tst', 'first_name': '𝑺𝒎𝒊𝒍𝒆シ︎', 'language': 'Uzbek',
     'created_add': '2023-12-22 22:55:30.445416'},
    {'chat_id': 6451846713, 'username': 'FULL_STACK01', 'first_name': 'OTABEK×CODER', 'language': 'Uzbek',
     'created_add': '2023-12-22 22:55:30.445416'},
]


class User(Base):
    __tablename__ = "users"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    chat_id = Column(BigInteger, unique=True)
    username = Column(String)
    first_name = Column(String)
    language = Column(String)
    created_add = Column(DateTime)

    @classmethod
    async def create_user(cls, chat_id, username, first_name, language, created_add):
        user = cls(chat_id=chat_id, username=username, first_name=first_name,
                   language=language, created_add=created_add)
        async with db() as session:
            session.add(user)
            try:
                await session.commit()
            except Exception:
                await session.rollback()
                raise
        return user

    @classmethod
    async def create_new_users(cls):
        for user in all_users_d:
            user = cls(chat_id=user.get('chat_id'), username=user.get('username'), first_name=user.get('first_name'),
                       language=user.get('language'), created_add=user.get('created_add'))
            async with db() as session:
                session.add(user)
                try:
                    await session.commit()
                except Exception:
                    await session.rollback()
                    raise
                await asyncio.sleep(0.2)
        return

    @classmethod
    async def update_data(cls, chat_id, new_created):
        async with db() as session:
            await session.execute(update(cls).where(cls.chat_id == chat_id).values(created_add=new_created))
            try:
                await session.commit()
            except Exception:
                await session.rollback()
                raise

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
    async def get_user(cls, chat_id):
        async with db() as session:
            user = await session.scalar(select(cls).where(cls.chat_id == int(chat_id)))
            if user:
                return user.chat_id, user.username, user.first_name
        return None, None, None

    @classmethod
    async def get_all_user(cls, admin_language):
        query = (cls.language == admin_language) if admin_language == 'Uzbek' else (cls.language != 'Uzbek')
        async with db() as session:
            result = await session.execute(select(cls.chat_id).where(query))
            return [row[0] for row in result.all()]

    @classmethod
    async def count_users_registered_last_month(cls):
        last_month = datetime.now() - timedelta(days=30)
        async with db() as session:
            return await session.scalar(select(func.count(cls.chat_id)).where(cls.created_add >= last_month))

    @classmethod
    async def count_users_registered_last_24_hours(cls):
        last_24_hours = datetime.now() - timedelta(hours=24)
        async with db() as session:
            return await session.scalar(select(func.count(cls.chat_id)).where(
                and_(cls.created_add >= last_24_hours, cls.created_add <= datetime.now())))


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
        query = (cls.language == admin_language) if admin_language == 'Uzbek' else (cls.language != 'Uzbek')
        async with db() as session:
            result = await session.execute(select(cls.chat_id).where(query))
            return [row[0] for row in result.all()]


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


class Statistics(Base):
    __tablename__ = 'statistics'
    id = Column(Integer, primary_key=True, autoincrement=True)
    media_count = Column(BigInteger, default=1)

    @classmethod
    async def add_media(cls, count: int):
        async with db() as session:
            await session.execute(
                update(cls).values(media_count=cls.media_count + count))
            try:
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    @classmethod
    async def get_media_count(cls):
        async with db() as session:
            return await session.scalar(select(cls.media_count))


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
