import os
import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.engine import Connection

from alembic import context
from dotenv import load_dotenv, find_dotenv

# -- 1) Загружаем .env прежде, чем брать URL
dotenv_path = find_dotenv()
print(">>> ALEMBIC: loading .env from", dotenv_path)
load_dotenv(dotenv_path, override=True)

# -- 2) Берём конфиг Alembic
config = context.config
print(">>> ALEMBIC: ini file =", config.config_file_name)
fileConfig(config.config_file_name)

# -- 3) Берём DATABASE_URL из окружения
db_url = os.getenv("DATABASE_URL")
print(">>> ALEMBIC: os.getenv('DATABASE_URL') =", repr(db_url))
if not db_url:
    raise RuntimeError("DATABASE_URL is not set in .env")

# Перекрываем URL в конфиге Alembic
config.set_main_option("sqlalchemy.url", db_url)
print(">>> ALEMBIC: final sqlalchemy.url =", config.get_main_option("sqlalchemy.url"))

# -- 4) Метаданные ваших моделей
from app.models import Base
target_metadata = Base.metadata

def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    print(">>> ALEMBIC OFFLINE MODE, using URL", url)
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(sync_conn: Connection):
    print(">>> ALEMBIC ONLINE MODE, running migrations on connection", sync_conn)
    context.configure(
        connection=sync_conn,
        target_metadata=target_metadata,
    )
    with context.begin_transaction():
        context.run_migrations()

async def run_async_migrations():
    url = config.get_main_option("sqlalchemy.url")
    print(">>> ALEMBIC ASYNC ENGINE URL =", url)
    engine = create_async_engine(
        url,
        poolclass=pool.NullPool,
        future=True,
    )
    async with engine.connect() as async_conn:
        print(">>> ALEMBIC: connected async_conn OK")
        await async_conn.run_sync(do_run_migrations)
    await engine.dispose()

def run_migrations_online():
    print(">>> ALEMBIC: run_migrations_online() start")
    asyncio.run(run_async_migrations())
    print(">>> ALEMBIC: run_migrations_online() done")

# Запуск
print(">>> ALEMBIC: context.is_offline_mode() =", context.is_offline_mode())
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()