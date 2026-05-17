import os

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5434/hr_db",
)

engine = create_async_engine(DATABASE_URL, echo=True)

session_factory = async_sessionmaker(
    bind=engine, autocommit=False, autoflush=False, expire_on_commit=False
)
