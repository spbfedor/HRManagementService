from sqlalchemy import (
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table
)
from sqlalchemy.orm import registry

from src.models import Department, Employee

mapper_registry = registry()
metadata = mapper_registry.metadata

departments_table = Table(
    "departments",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("name", String(200), nullable=False),
    Column(
        "parent_id",
        Integer,
        ForeignKey("departments.id", ondelete="CASCADE"),
        nullable=True,
    ),
    Column("created_at", DateTime, nullable=False),
)

employees_table = Table(
    "employees",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column(
        "department_id",
        Integer,
        ForeignKey("departments.id", ondelete="CASCADE"),
        nullable=False,
    ),
    Column("full_name", String(200), nullable=False),
    Column("position", String(200), nullable=False),
    Column("hired_at", Date, nullable=True),
    Column("created_at", DateTime, nullable=False),
)


def start_mappers():
    if not mapper_registry.mappers:
        mapper_registry.map_imperatively(Employee, employees_table)
        mapper_registry.map_imperatively(Department, departments_table)
