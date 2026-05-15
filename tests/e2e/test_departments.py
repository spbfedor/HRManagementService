import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_creation_of_a_department(client: AsyncClient):
    payload = {"name": "Office"}
    response = await client.post("/departments/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Office"
    assert "id" in data