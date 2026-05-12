from datetime import datetime

from src.models import Department, Employee


def test_create_department_entity():
    now = datetime.now()
    department = Department(
        id=1,
        name="Financial dep",
        created_at=now
    )
    assert department.id == 1
    assert department.name == "Financial dep"
    assert department.parent_id is None
    assert department.created_at == now
    assert department.employees == []