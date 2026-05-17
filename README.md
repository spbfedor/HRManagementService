# HR Management Service

A production-ready, asynchronous microservice for managing hierarchical department trees and employee assignments. Built with **FastAPI**, **SQLAlchemy 2.0 (Classical Imperative Mapping)**, and **PostgreSQL**, following the strict guidelines of **Clean Architecture** and Domain-Driven Design (DDD).

[![Code Style: Black](https://shields.io)](https://github.com)
[![Imports: isort](https://shields.io)](https://github.io)
[![Linting: flake8](https://shields.io)](https://pycqa.org)

---

## 🏗️ Architectural Blueprint

The codebase is strictly separated into independent layers in accordance with Harry Percival's *"Architecture Patterns with Python"* (Cosmic Python):

```text
    ┌─────────────────────────────────────────────────────────┐
    │                    Presentation Layer                   │
    │               (FastAPI Routers & Pydantic V2)           │
    └────────────────────────────┬────────────────────────────┘
                                 │ (invokes)
    ┌────────────────────────────▼────────────────────────────┐
    │                      Service Layer                      │
    │         (Orchestrates UoW & Application Logic)          │
    └────────────────────────────┬────────────────────────────┘
                                 │ (coordinates)
    ┌────────────────────────────▼────────────────────────────┐
    │                     Data Access Layer                   │
    │          (Abstract Repositories & SQL UoW)              │
    └────────────────────────────┬────────────────────────────┘
                                 │ (maps data via Registry)
    ┌────────────────────────────▼────────────────────────────┐
    │                       Domain Model                      │
    │         (Pure Python Dataclasses / Enterprise Rules)     │
    └─────────────────────────────────────────────────────────┘
```

### Core Architecture Components:
*   **Domain Model (`src/models/`)**: Pure Python dataclasses completely isolated from any database or framework concerns. All business rules (e.g., string trimming, non-empty text validation) are encapsulated directly within the entities' `__post_init__`.
*   **Data Access Layer (`src/adapters/`)**: 
    *   *Classical Imperative Mapping*: Implemented using SQLAlchemy 2.0's `registry.map_imperatively`, mapping standard db tables onto the domain objects without bleeding database decorators into the domain code.
    *   *Repository Pattern*: Abstracts database interaction away from the business layer.
*   **Service Layer & Unit of Work (`src/services/`)**: Orchestrates transactions and coordinates atomicity. Service functions are completely agnostic of the real DB driver. Tree pruning, name uniqueness inside a specific node, and cyclic dependency prevention rules are handled here.

---

## 🛠️ Tech Stack & Code Quality

*   **Runtime**: Python 3.12 / FastAPI (utilizing modern `lifespan` context manager)
*   **Database Stack**: PostgreSQL 15 + `asyncpg` (Fully asynchronous CRUD operations)
*   **Migrations**: Asynchronous Alembic workflow (`alembic init -t async`)
*   **Quality Gates**:
    *   **Strict PEP 8 enforcement**: Lines limited strictly to **79 characters**.
    *   Formatters: `black --line-length=79`, `isort`.
    *   Linter: `flake8` clean configuration (0 errors, 0 warnings).

---

## ⚡ Quick Start & Deployment

The infrastructure is fully dockerized with embedded database healthchecks ensuring proper orchestration sequence.

### Prerequisites
Create a `.env` file in the root directory:
```ini
DB_USER=postgres
DB_PASSWORD=postgres
DB_NAME=hr_db
```

### Production Up & Build
Run the following command to bootstrap the database container, execute asynchronous Alembic migrations, and spin up the ASGI app server:
```bash
docker compose up --build
```

Once initialized, the API Interactive Documentation will be fully available at:
👉 **http://localhost:8000/docs** (Swagger UI)

---

## 🧪 Testing Strategy

The project contains a test suite covering domain components, API schemas, and End-to-End database workflows. E2E execution hooks into an isolated asynchronous routine, triggering state truncations (`TRUNCATE ... CASCADE`) between individual test tasks to prevent side-effects.

To run the full test suite locally within your activated virtual environment:
```bash
python -m pytest
```

### Test Suite Execution Output:
```text
collected 36 items

tests/e2e/test_departments.py .                                          [ 11%]
tests/unit/api/test_department_schemas.py .......                        [ 30%]
tests/unit/api/test_employee_schemas.py ...............                  [ 72%]
tests/unit/domain/test_model_department.py .....                         [ 86%]
tests/unit/domain/test_model_employee.py .....                           [100%]

========================== 36 passed in 1.15s ==========================
```
