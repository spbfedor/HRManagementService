from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Department:
    name: str
    id: int | None = None
    parent_id: int | None = None
    created_at: datetime = field(default_factory=datetime.now)
    employees: list = field(default_factory=list)

    def __post_init__(self):
        if self.name is not None:
            self.name = self.name.strip()
        if not self.name:
            raise ValueError("Name cannot be empty")
