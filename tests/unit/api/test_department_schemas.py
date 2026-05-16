import pytest
from pydantic import ValidationError
from src.schemas import DepartmentCreate, DepartmentUpdate


def test_for_successful_creation():
    payload = {"name": "Financial dep", "parent_id": 1}
    schema = DepartmentCreate(**payload)

    assert schema.name == "Financial dep"
    assert schema.parent_id == 1

def test_for_successful_creation_without_parent():
    payload = {"name": "Financial dep"}
    schema = DepartmentCreate(**payload)

    assert schema.parent_id is None

def test_whitespace_trimming():
    payload = {"name": " QA  "}
    schema = DepartmentCreate(**payload)

    assert schema.name == "QA"

@pytest.mark.parametrize(
    "invalid_name",
    [
        "",
        "   ",
        "q" * 201,
    ]
)
def test_create_name_validation(invalid_name):
    payload =  {"name": invalid_name, "parent_id": 1}
    with pytest.raises(ValidationError):
        DepartmentCreate(**payload)

def test_partial_update():
    payload = {"name": "New Name"}
    schema = DepartmentUpdate(**payload)

    update_data = schema.model_dump(exclude_unset=True)

    assert "name" in update_data
    assert update_data["name"] == "New Name"
    assert "parent_id" not in update_data