from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

from src.schemas.employees import EmployeeRead


class DepartmentCreate(BaseModel):
    name: Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=1, max_length=200),
    ]
    parent_id: int | None = None


class DepartmentUpdate(BaseModel):
    name: Annotated[
        str | None,
        StringConstraints(strip_whitespace=True, min_length=1, max_length=200),
    ] = None
    parent_id: int | None = None


class DepartmentRead(BaseModel):
    id: int
    name: str
    created_at: datetime
    parent_id: int | None = None
    employees: list[EmployeeRead] = Field(default_factory=list)
    children: list["DepartmentRead"] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
