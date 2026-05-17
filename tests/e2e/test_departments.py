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


@pytest.mark.asyncio
async def test_get_department_tree_with_depth(client: AsyncClient):
    hq = await client.post("/departments/", json={"name": "HQ"})
    hq_id = hq.json()["id"]

    dev = await client.post(
        "/departments/", json={"name": "Development", "parent_id": hq_id}
    )
    dev_id = dev.json()["id"]

    await client.post(
        "/departments/", json={"name": "Python Team", "parent_id": dev_id}
    )

    response = await client.get(
        f"/departments/{hq_id}?depth=2&include_employees=false"
    )
    assert response.status_code == 200
    data = response.json()

    assert len(data["children"]) == 1
    assert data["children"][0]["name"] == "Development"
    assert len(data["children"][0]["children"]) == 0


@pytest.mark.asyncio
async def test_patch_cyclic_dependency_raises_conflict(client: AsyncClient):
    hq = await client.post("/departments/", json={"name": "HQ"})
    hq_id = hq.json()["id"]

    dev = await client.post(
        "/departments/", json={"name": "Development", "parent_id": hq_id}
    )
    dev_id = dev.json()["id"]

    response = await client.patch(
        f"/departments/{hq_id}",
        json={"parent_id": dev_id}
    )

    assert response.status_code == 409
    assert "Cyclic dependency" in response.json()["detail"]


@pytest.mark.asyncio
async def test_delete_department_in_cascade_mode(client: AsyncClient):
    dept = await client.post("/departments/", json={"name": "Trash Dept"})
    dept_id = dept.json()["id"]

    await client.post(
        f"/departments/{dept_id}/employees/",
        json={
            "full_name": "Frodo",
            "position": "Baggins",
            "hired_at": "2026-05-17",
        },
    )

    delete_resp = await client.delete(f"/departments/{dept_id}?mode=cascade")
    assert delete_resp.status_code == 204

    get_resp = await client.get(f"/departments/{dept_id}")
    assert get_resp.status_code == 404
