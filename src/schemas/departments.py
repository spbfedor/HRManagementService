from typing import Annotated
from pydantic import BaseModel, Field, StringConstraints



class DepartmentCreate(BaseModel):
    name: Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=1, max_length=200)
    ]
    parent_id: int | None = None


class DepartmentUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
        str_strip=True
    )
    parent_id: int | None = None