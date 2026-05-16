from datetime import date
from typing import Annotated

from pydantic import BaseModel, StringConstraints


class EmployeeCreate(BaseModel):
    full_name: Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=1, max_length=200)
    ]
    position: Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=1, max_length=200)
    ]
    hired_at: date | None = None