import pytest
from datetime import date, datetime

from src.models import Employee


def test_create_employee_entity():
    now = datetime.now()
    employee = Employee(
        id=1,
        department_id=1,
        full_name="Frodo Baggins",
        position="manager",
        hired_at=date.today(),
        created_at=now
    )
    assert employee.id == 1
    assert employee.department_id == 1
    assert employee.full_name == "Frodo Baggins"
    assert employee.position == "manager"
    assert employee.hired_at == date.today()
    assert employee.created_at == now


@pytest.mark.parametrize(
        "full_name, position, excepted_error",
        [
            ("", "manager", "The 'full_name' field cannot be empty"),
            ("    ", "manager", "The 'full_name' field cannot be empty"),
            ("Frodo Baggins", "", "The 'position' field cannot be empty"),
            ("Frodo Baggins", "   ", "The 'position' field cannot be empty")
        ]
)
def test_employee_validation_errors(full_name, position, excepted_error):
    with pytest.raises(ValueError) as ex:
        Employee(department_id=1, full_name=full_name, position=position)
    assert str(ex.value) == excepted_error
