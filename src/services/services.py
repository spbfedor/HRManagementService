import logging
from datetime import datetime
from typing import Optional

from src.models import Department, Employee
from src.schemas.departments import DepartmentCreate, DepartmentUpdate
from src.schemas.employees import EmployeeCreate
from src.services.unit_of_work import AbstractUnitOfWork


logger = logging.getLogger(__name__)


class DomainException(Exception):
    ...


class NotFoundException(DomainException):
    ...


class ConflictException(DomainException):
    ...


def _prune_tree(department: dict, max_depth: int, current_depth: int = 1):
    if current_depth >= max_depth:
        department["children"] = []
        return
    for child in department["children"]:
        _prune_tree(child, max_depth, current_depth + 1)


async def create_department(
    uow: AbstractUnitOfWork, data: DepartmentCreate
) -> Department:
    async with uow:
        all_depts = await uow.departments.list_all()
        for d in all_depts:
            if (
                d.parent_id == data.parent_id
                and d.name.lower() == data.name.lower()
            ):
                logger.warning(
                    (
                        "Попытка создать дубликат "
                        "департамента '%s' для parent_id=%s"
                    ),
                    data.name,
                    data.parent_id,
                )
                raise ConflictException(
                    f"Department with name '{data.name}' "
                    f"already exists under this parent"
                )

        if data.parent_id is not None:
            parent = await uow.departments.get_by_id(data.parent_id)
            if not parent:
                raise NotFoundException(
                    f"Parent department with id {data.parent_id} not found"
                )

        department = Department(
            name=data.name,
            parent_id=data.parent_id,
            created_at=datetime.now()
        )
        await uow.departments.add(department)
        await uow.commit()

        logger.info(
            "Успешно создан департамент: %s (ID: %s)",
            department.name,
            department.id,
        )
        return department


async def get_department_tree(
    uow: AbstractUnitOfWork,
    department_id: int,
    depth: int,
    include_employees: bool,
) -> Department:
    async with uow:
        if depth > 5:
            depth = 5

        root_dept = await uow.departments.get_with_tree(
            department_id=department_id,
            depth=depth,
            include_employees=include_employees,
        )
        if not root_dept:
            logger.error(
                "Департамент с ID=%s не найден при запросе дерева",
                department_id,
            )
            raise NotFoundException(
                f"Department with id {department_id} not found"
            )

        _prune_tree(root_dept, depth)
        return root_dept


async def update_department(
    uow: AbstractUnitOfWork, department_id: int, data: DepartmentUpdate
) -> Department:
    async with uow:
        department = await uow.departments.get_by_id(department_id)
        if not department:
            raise NotFoundException(
                f"Department with id {department_id} not found"
            )

        all_depts = await uow.departments.list_all()

        if data.parent_id is not None or "parent_id" in data.model_fields_set:
            new_parent_id = data.parent_id

            if new_parent_id == department_id:
                raise ConflictException(
                    "A department cannot be its own parent"
                )

            if new_parent_id is not None:
                dept_map = {d.id: d for d in all_depts if d.id is not None}
                if new_parent_id not in dept_map:
                    raise NotFoundException(
                        f"Parent department with id {new_parent_id} not found"
                    )

                current_check_id = new_parent_id
                while current_check_id is not None:
                    if current_check_id == department_id:
                        logger.warning(
                            (
                                "Обнаружен цикл! Перемещение ID=%s "
                                "внутрь поддерева заблокировано"
                            ),
                            department_id,
                        )
                        raise ConflictException(
                            "Cyclic dependency detected: "
                            "cannot move into its own subtree"
                        )
                    parent_obj = dept_map.get(current_check_id)
                    if parent_obj:
                        current_check_id = parent_obj.parent_id
                    else:
                        current_check_id = None

            department.parent_id = new_parent_id

        if data.name is not None:
            current_parent = department.parent_id
            for d in all_depts:
                if (
                    d.id != department_id
                    and d.parent_id == current_parent
                    and d.name.lower() == data.name.lower()
                ):
                    raise ConflictException(
                        f"Department with name '{data.name}' "
                        f"already exists under this parent"
                    )
            department.name = data.name.strip()

        await uow.commit()
        logger.info("Департамент ID=%s успешно обновлен", department_id)
        return department


async def delete_department(
    uow: AbstractUnitOfWork,
    department_id: int,
    mode: str,
    reassign_to_id: Optional[int] = None,
) -> None:
    async with uow:
        department = await uow.departments.get_by_id(department_id)
        if not department:
            raise NotFoundException(
                f"Department with id {department_id} not found"
            )

        if mode == "reassign":
            if reassign_to_id is None:
                raise DomainException(
                    "reassign_to_department_id is "
                    "required when mode is 'reassign'"
                )

            if reassign_to_id == department_id:
                raise ConflictException(
                    "Cannot reassign employees to "
                    "the department being deleted"
                )

            target_dept = await uow.departments.get_by_id(reassign_to_id)
            if not target_dept:
                raise NotFoundException(
                    f"Target reassign department "
                    f"with id {reassign_to_id} not found"
                )

            await uow.employees.reassign_employees(
                from_dept_id=department_id, to_dept_id=reassign_to_id
            )
            logger.info(
                "Сотрудники из департамента ID=%s переведены в ID=%s",
                department_id,
                reassign_to_id,
            )

        await uow.departments.delete(department_id)
        await uow.commit()
        logger.info(
            "Департамент ID=%s успешно "
            "удален в режиме %s",
            department_id,
            mode
        )


async def create_employee(
    uow: AbstractUnitOfWork, department_id: int, data: EmployeeCreate
) -> Employee:
    async with uow:
        department = await uow.departments.get_by_id(department_id)
        if not department:
            logger.error(
                "Попытка создать сотрудника в "
                "несуществующем подразделении ID=%s",
                department_id,
            )
            raise NotFoundException(
                f"Department with id {department_id} not found"
            )

        employee = Employee(
            department_id=department_id,
            full_name=data.full_name,
            position=data.position,
            hired_at=data.hired_at,
            created_at=datetime.now(),
        )
        await uow.employees.add(employee)
        await uow.commit()

        logger.info(
            "Создан сотрудник %s в отделе ID=%s",
            employee.full_name,
            department_id,
        )
        return employee
