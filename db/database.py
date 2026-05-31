import os

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs
from sqlalchemy.orm import DeclarativeBase


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_DIR = os.path.join(BASE_DIR, "db")
DB_PATH = os.path.join(DB_DIR, "database.db")
DATABASE_URL = f"sqlite+aiosqlite:///{DB_PATH}"


class Base(AsyncAttrs, DeclarativeBase):
    pass


engine = create_async_engine(DATABASE_URL, echo = False)

AsyncSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False
)

async def init_db():
    os.makedirs(DB_DIR, exist_ok=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)