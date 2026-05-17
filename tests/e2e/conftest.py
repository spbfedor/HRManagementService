import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text

from src.adapters.orm import start_mappers
from src.core.database import engine
from src.main import app


@pytest_asyncio.fixture(scope="function")
async def client():
    try:
        start_mappers()
    except Exception:
        pass

    await engine.dispose()

    async with engine.begin() as conn:
        await conn.execute(
            text(
                "TRUNCATE TABLE departments, "
                "employees RESTART IDENTITY CASCADE;"
            )
        )

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac

    await engine.dispose()
