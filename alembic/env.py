import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import URL
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import AsyncEngine, async_engine_from_config

from app.utils.config import PostgresConfig
from app.db.models.base import Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def _get_postgres_dsn() -> URL:
    # noinspection PyArgumentList
    _config: PostgresConfig = PostgresConfig()
    return _config.build_url()


# print(_get_postgres_dsn())
# config.set_main_option("sqlalchemy.url", _get_postgres_dsn())


def run_migrations_offline() -> None:
    # url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=_get_postgres_dsn(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def _get_connectable() -> AsyncEngine:
    section = config.get_section(config.config_ini_section, {})
    # if getattr(conf.db, "use_pgbouncer", False):
    #     return async_engine_from_config(
    #         section,
    #         prefix="sqlalchemy.",
    #         poolclass=pool.NullPool,
    #         url=conf.db.sqlalchemy_url(),
    #     )
    # else:
    return async_engine_from_config(
        section,
        prefix="sqlalchemy.",
        url=_get_postgres_dsn(),
    )


async def run_async_migrations() -> None:
    connectable = await _get_connectable()

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
