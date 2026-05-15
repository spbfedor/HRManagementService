import pytest_asyncio

from httpx import ASGITransport, AsyncClient

from src.main import app


@pytest_asyncio.fixture(scope="function")
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://test"
    ) as client:
        yield client