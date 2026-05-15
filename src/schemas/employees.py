from datetime import date

from pydantic import BaseModel, Field


class EmployeeCreate(BaseModel):
    full_name: str = Field(min_length=1, max_length=200, str_strip=True)
    position: str = Field(min_length=1, max_length=200, str_strip=True)
    hired_at: date | None = None