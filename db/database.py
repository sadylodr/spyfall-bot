from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs
from sqlalchemy.orm import DeclarativeBase


DATABASE_URL = "sqlite+aiosqlite:///data/database.db"


class Base(AsyncAttrs, DeclarativeBase):
    pass


engine = create_async_engine(DATABASE_URL, echo = False)

AsyncSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False
)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)