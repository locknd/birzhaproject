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
load_dotenv(dotenv_path, override=True)

# -- 2) Берём конфиг Alembic и устанавливаем реальный URL
config = context.config
fileConfig(config.config_file_name)

db_url = os.getenv("DATABASE_URL")
if not db_url:
    raise RuntimeError("DATABASE_URL is not set in .env")
# ВАЖНО: говорим Alembic, куда подключаться
config.set_main_option("sqlalchemy.url", db_url)

# -- 3) Ваши метаданные
from app.models import Base
target_metadata = Base.metadata

def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(sync_conn: Connection):
    context.configure(
        connection=sync_conn,
        target_metadata=target_metadata,
    )
    with context.begin_transaction():
        context.run_migrations()

async def run_async_migrations():
    url = config.get_main_option("sqlalchemy.url")
    engine = create_async_engine(
        url,
        poolclass=pool.NullPool,
        future=True,
    )
    async with engine.connect() as async_conn:
        await async_conn.run_sync(do_run_migrations)
    await engine.dispose()

def run_migrations_online():
    asyncio.run(run_async_migrations())

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()