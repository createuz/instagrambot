from __future__ import annotations

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncEngine,
    AsyncSession,
)

from app.db.config import AppConfig


def build_async_engine(config: AppConfig) -> AsyncEngine:
    return create_async_engine(
        url=config.postgres.build_url(),
        echo=config.sql_alchemy.echo,
        echo_pool=config.sql_alchemy.echo_pool,
        pool_size=config.sql_alchemy.pool_size,
        max_overflow=config.sql_alchemy.max_overflow,
        pool_timeout=config.sql_alchemy.pool_timeout,
        pool_recycle=config.sql_alchemy.pool_recycle,
        pool_pre_ping=True,
        future=True,
    )


def create_session_pool(config: AppConfig) -> async_sessionmaker[AsyncSession]:
    engine: AsyncEngine = build_async_engine(config)
    return async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )
