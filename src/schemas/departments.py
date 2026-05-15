from pydantic import BaseModel, Field


class DepartmentCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200, str_strip=True)
    parent_id: int | None = None


class DepartmentUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
        str_strip=True
    )
    parent_id: int | None = None