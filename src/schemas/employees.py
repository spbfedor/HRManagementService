from datetime import date, datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, StringConstraints


class EmployeeCreate(BaseModel):
    full_name: Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=1, max_length=200),
    ]
    position: Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=1, max_length=200),
    ]
    hired_at: date | None = None


class EmployeeRead(BaseModel):
    id: int
    department_id: int
    full_name: str
    position: str
    hired_at: date | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
