from datetime import datetime

import pytest

from src.models import Department


def test_create_department_entity():
    now = datetime.now()
    department = Department(id=1, name="Financial dep", created_at=now)
    assert department.id == 1
    assert department.name == "Financial dep"
    assert department.parent_id is None
    assert department.created_at == now
    assert department.employees == []


@pytest.mark.parametrize(
    "name, expected_error",
    [("", "Name cannot be empty"), ("   ", "Name cannot be empty")],
)
def test_for_an_empty_name_field(name, expected_error):
    with pytest.raises(ValueError) as ex:
        Department(name=name)
    assert str(ex.value) == expected_error


def test_to_remove_extra_spaces():
    department = Department(name="  Financial dep  ")
    assert department.name == "Financial dep"


def test_tree_creation_check():
    parent_dep = Department(id=1, name="Supply")
    child_dep = Department(name="Warehouse", parent_id=parent_dep.id)
    assert child_dep.parent_id == 1
