from abc import ABC, abstractmethod
from typing import List, Optional

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.orm import departments_table, employees_table
from src.models import Department, Employee


class AbstractDepartmentRepository(ABC):
    @abstractmethod
    async def add(self, department: Department) -> None:
        ...

    @abstractmethod
    async def get_by_id(self, department_id: int) -> Optional[Department]:
        ...

    @abstractmethod
    async def list_all(self) -> List[Department]:
        ...

    @abstractmethod
    async def delete(self, department_id: int) -> None:
        ...

    @abstractmethod
    async def get_with_tree(
        self, department_id: int, depth: int, include_employees: bool
    ) -> Optional[Department]:
        ...


class AbstractEmployeeRepository(ABC):
    @abstractmethod
    async def add(self, employee: Employee) -> None:
        ...

    @abstractmethod
    async def reassign_employees(
        self,
        from_dept_id: int,
        to_dept_id: int
    ) -> None: ...


class SqlAlchemyDepartmentRepository(AbstractDepartmentRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, department: Department) -> None:
        self.session.add(department)

    async def get_by_id(self, department_id: int) -> Optional[Department]:
        result = await self.session.execute(
            select(Department).where(departments_table.c.id == department_id)
        )
        return result.scalar_one_or_none()

    async def list_all(self) -> List[Department]:
        result = await self.session.execute(select(Department))
        return list(result.scalars().all())

    async def delete(self, department_id: int) -> None:
        await self.session.execute(
            delete(departments_table).where(
                departments_table.c.id == department_id
            )
        )

    async def get_with_tree(
        self, department_id: int, depth: int, include_employees: bool
    ) -> Optional[dict]:
        dept_result = await self.session.execute(select(Department))
        all_depts = dept_result.scalars().all()

        dept_map = {}
        root_dept_dict = None

        for d in all_depts:
            d_dict = {
                "id": d.id,
                "name": d.name,
                "parent_id": d.parent_id,
                "created_at": d.created_at,
                "employees": [],
                "children": [],
            }
            dept_map[d.id] = d_dict
            if d.id == department_id:
                root_dept_dict = d_dict

        if not root_dept_dict:
            return None

        if include_employees:
            emp_result = await self.session.execute(select(Employee))
            all_emps = emp_result.scalars().all()
            for emp in all_emps:
                if emp.department_id in dept_map:
                    dept_map[emp.department_id]["employees"].append(
                        {
                            "id": emp.id,
                            "department_id": emp.department_id,
                            "full_name": emp.full_name,
                            "position": emp.position,
                            "hired_at": emp.hired_at,
                            "created_at": emp.created_at,
                        }
                    )

        for d in all_depts:
            if d.parent_id and d.parent_id in dept_map:
                dept_map[d.parent_id]["children"].append(dept_map[d.id])

        return root_dept_dict


class SqlAlchemyEmployeeRepository(AbstractEmployeeRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, employee: Employee) -> None:
        self.session.add(employee)

    async def reassign_employees(
        self,
        from_dept_id: int,
        to_dept_id: int
    ) -> None:
        await self.session.execute(
            update(employees_table)
            .where(employees_table.c.department_id == from_dept_id)
            .values(department_id=to_dept_id)
        )
