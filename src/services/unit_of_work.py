from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.repository import (
    AbstractDepartmentRepository,
    AbstractEmployeeRepository,
    SqlAlchemyDepartmentRepository,
    SqlAlchemyEmployeeRepository,
)
from src.core.database import session_factory


class AbstractUnitOfWork(ABC):
    departments: AbstractDepartmentRepository
    employees: AbstractEmployeeRepository

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.rollback()

    @abstractmethod
    async def commit(self):
        ...

    @abstractmethod
    async def rollback(self):
        ...


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    def __init__(self, session_factory=session_factory):
        self.session_factory = session_factory

    async def __aenter__(self):
        self.session: AsyncSession = self.session_factory()

        self.departments = SqlAlchemyDepartmentRepository(self.session)
        self.employees = SqlAlchemyEmployeeRepository(self.session)
        return await super().__aenter__()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            await super().__aexit__(exc_type, exc_val, exc_tb)
        finally:
            await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()
