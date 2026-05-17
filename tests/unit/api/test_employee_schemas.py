from datetime import date

import pytest
from pydantic import ValidationError

from src.schemas import EmployeeCreate


def test_for_successful_creation():
    payload = {
        "full_name": "Frodo Baggins",
        "position": "Manager",
        "hired_at": "2026-05-16",
    }
    schema = EmployeeCreate(**payload)

    assert schema.full_name == "Frodo Baggins"
    assert schema.position == "Manager"
    assert schema.hired_at == date(2026, 5, 16)


def test_for_successful_creation_without_hired_at():
    payload = {
        "full_name": "Frodo Baggins",
        "position": "Manager",
    }
    schema = EmployeeCreate(**payload)
    assert schema.hired_at is None


def test_whitespace_trimming():
    payload = {
        "full_name": "  Frodo Baggins ",
        "position": " Manager  ",
    }
    schema = EmployeeCreate(**payload)
    assert schema.full_name == "Frodo Baggins"
    assert schema.position == "Manager"


@pytest.mark.parametrize(
    "invalid_data",
    [
        {"full_name": ""},
        {"full_name": "   "},
        {"position": ""},
        {"position": "   "},
        {"full_name": "q" * 201},
        {"position": "q" * 201},
    ],
)
def test_create_validation_errors(invalid_data):
    payload = {
        "full_name": "Frodo Baggins",
        "position": "Manager",
        "hired_at": "2026-05-16",
    }
    payload.update(invalid_data)

    with pytest.raises(ValidationError):
        EmployeeCreate(**payload)


@pytest.mark.parametrize(
    "invalid_data",
    [
        "хорошего-вам-вечера",
        "   ",
        "2026-14-12",
        "2026-02-30",
        "16/05/2026",
        "16.05.2026",
    ],
)
def test_create_date_validation(invalid_data):
    payload = {
        "full_name": "Frodo Baggins",
        "position": "Manager",
        "hired_at": invalid_data,
    }
    with pytest.raises(ValidationError):
        EmployeeCreate(**payload)
