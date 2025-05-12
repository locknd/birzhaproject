import os
import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.engine import Connection

from alembic import context
from dotenv import load_dotenv, find_dotenv

# 1) Загружаем .env, перезаписывая переменные окружения
dotenv_path = find_dotenv()
load_dotenv(dotenv_path, override=True)

# 2) Конфиг Alembic (из alembic.ini, без sqlalchemy.url там)
config = context.config
fileConfig(config.config_file_name)

# 3) Метаданные ваших моделей
from app.models import Base
target_metadata = Base.metadata

def run_migrations_offline():
    url = os.getenv("DATABASE_URL")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(sync_conn: Connection):
    """
    Запускает миграции в синхронном контексте
    (Alembic не знает про asyncio).
    """
    context.configure(
        connection=sync_conn,
        target_metadata=target_metadata
    )
    with context.begin_transaction():
        context.run_migrations()

async def run_async_migrations():
    """
    Оболочка для асинхронного движка:
    создаём AsyncEngine, подключаемся async with,
    и отдаем sync_conn внутрь do_run_migrations.
    """
    engine = create_async_engine(
        os.getenv("DATABASE_URL"),
        poolclass=pool.NullPool,
        future=True,
    )
    async with engine.connect() as async_conn:
        # .run_sync() переключает в sync_conn и вызывает do_run_migrations
        await async_conn.run_sync(do_run_migrations)
    await engine.dispose()

def run_migrations_online():
    # Запускаем асинхронную обёртку через asyncio.run
    asyncio.run(run_async_migrations())

# Выбор режима
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()