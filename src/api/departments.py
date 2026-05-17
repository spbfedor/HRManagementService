from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status

from src import services
from src.schemas.departments import (
    DepartmentCreate,
    DepartmentRead,
    DepartmentUpdate
)
from src.schemas.employees import EmployeeCreate
from src.services import unit_of_work

router = APIRouter(prefix="/departments", tags=["Departments"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_department(data: DepartmentCreate):
    uow = unit_of_work.SqlAlchemyUnitOfWork()
    return await services.create_department(uow, data)


@router.post("/{id}/employees/", status_code=status.HTTP_201_CREATED)
async def create_employee(id: int, data: EmployeeCreate):
    uow = unit_of_work.SqlAlchemyUnitOfWork()
    return await services.create_employee(uow, id, data)


@router.get("/{id}")
async def get_department_tree(
    id: int,
    depth: int = Query(1, ge=1, le=5),
    include_employees: bool = Query(True),
):
    uow = unit_of_work.SqlAlchemyUnitOfWork()
    dept = await services.get_department_tree(
        uow,
        id,
        depth,
        include_employees
    )

    return DepartmentRead.model_validate(dept, from_attributes=True)


@router.patch("/{id}")
async def update_department(id: int, data: DepartmentUpdate):
    uow = unit_of_work.SqlAlchemyUnitOfWork()
    return await services.update_department(uow, id, data)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_department(
    id: int,
    mode: str = Query(..., pattern="^(cascade|reassign)$"),
    reassign_to_department_id: Optional[int] = Query(None),
):
    if mode == "reassign" and reassign_to_department_id is None:
        raise HTTPException(
            status_code=400,
            detail=(
                "reassign_to_department_id " "is "
                "required when mode is 'reassign'"
            ),
        )
    uow = unit_of_work.SqlAlchemyUnitOfWork()
    await services.delete_department(uow, id, mode, reassign_to_department_id)
    return {"status": "success"}
