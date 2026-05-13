from dataclasses import dataclass, field
from datetime import date, datetime


@dataclass
class Employee:
    department_id: int
    full_name: str
    position: str
    id: int | None = None
    hired_at: date | None = None
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        if self.full_name is not None:
            self.full_name = self.full_name.strip()
        if not self.full_name:
            raise ValueError("The 'full_name' field cannot be empty")
        if self.position is not None:
            self.position = self.position.strip()
        if not self.position:
            raise ValueError("The 'position' field cannot be empty")
