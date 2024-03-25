from data import *

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class AsyncDatabaseSession:
    def __init__(self):
        self._session = None
        self._engine = None

    def __getattr__(self, name):
        return getattr(self._session, name)

    def __call__(self):
        return self._session

    def init(self):
        self._engine = create_async_engine(DB_URL, future=True, echo=True)
        self._session = async_sessionmaker(self._engine, expire_on_commit=False, class_=AsyncSession)()

    async def create_all(self):
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)


db = AsyncDatabaseSession()
