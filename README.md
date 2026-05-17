# HR Management Service

A production-ready, asynchronous microservice for managing hierarchical department trees and employee assignments. Built with **FastAPI**, **SQLAlchemy 2.0 (Classical Imperative Mapping)**, and **PostgreSQL**, following the principles of **Clean Layered Architecture** and Domain-Driven Design (DDD).

[![Code Style: Black](https://shields.io)](https://github.com)
[![Imports: isort](https://shields.io)](https://github.io)
[![Linting: flake8](https://shields.io)](https://pycqa.org)

---

## 🏗️ Architectural Blueprint

The codebase is strictly separated into independent layers to isolate business logic from frameworks and infrastructure:

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
    └─────────────────────────── ─────────────────────────────┘
```

### Layer Responsibilities:
*   **Domain Model (`src/models/`)**: Pure Python dataclasses completely isolated from data access concerns. All core enterprise rules (e.g., automatic string trimming, non-empty validation) are encapsulated inside the entities' `__post_init__`.
*   **Data Access Layer (`src/adapters/`)**: Implements the Repository pattern and classical imperative mapping (`registry.map_imperatively`) to keep entities untainted by database logic.
*   **Service Layer & Unit of Work (`src/services/`)**: Orchestrates atomic operations, enforces unique constraints within a specific hierarchy level, and runs the recursive protection check against cyclic dependencies.

---

## ⚡ Quick Start & Deployment

### Prerequisites
Create a `.env` file in the root directory:
```ini
DB_USER=postgres
DB_PASSWORD=postgres
DB_NAME=hr_db
```

### Production Bootstrap
Run the following command to spin up the database container, automatically apply asynchronous Alembic migrations, and start the app server:
```bash
docker compose up --build
```

Once initialized, the Interactive OpenAPI Documentation will be fully available at:
👉 **http://localhost:8000/docs** (Swagger UI)

---

## 🕹️ API Usage Examples & Core Workflows

Below are standard HTTP execution flows covering all specific business rules defined in the service requirements.

### 1. Create a Root Department
*   **HTTP Method**: `POST /departments/`
*   **Payload**:
    ```json
    {
      "name": "   HQ Department   "
    }
    ```
*   **Business Behavior**: Input strings are automatically whitespace-trimmed. Returns `201 Created` with `id: 1` and `name: "HQ Department"`. Sending the exact same request again will trigger a validation gate and return a `409 Conflict`.

### 2. Create a Sub-Department
*   **HTTP Method**: `POST /departments/`
*   **Payload** (linking to the parent created above):
    ```json
    {
      "name": "Engineering",
      "parent_id": 1
    }
    ```

### 3. Add an Employee to a Department
*   **HTTP Method**: `POST /departments/2/employees/`
*   **Payload**:
    ```json
    {
      "full_name": "  Legolas Greenleaf  ",
      "position": "Senior Core Dev",
      "hired_at": "2026-05-17"
    }
    ```
*   **Business Behavior**: `full_name` and `position` are automatically stripped of extra spaces. Returns `201 Created`. Sending an assignment to a non-existent department ID will throw a `404 Not Found`.

### 4. Fetch Hierarchical Tree (with Depth Control)
*   **HTTP Method**: `GET /departments/1?depth=2&include_employees=true`
*   **Response (`200 OK`)**:
    ```json
    {
      "id": 1,
      "name": "HQ Department",
      "parent_id": null,
      "created_at": "2026-05-17T21:40:00",
      "employees": [],
      "children": [
        {
          "id": 2,
          "name": "Engineering",
          "parent_id": 1,
          "created_at": "2026-05-17T21:42:00",
          "employees": [
            {
              "id": 1,
              "department_id": 2,
              "full_name": "Legolas Greenleaf",
              "position": "Senior Core Dev",
              "hired_at": "2026-05-17",
              "created_at": "2026-05-17T21:45:00"
            }
          ],
          "children": []
        }
      ]
    }
    ```
*   **Business Behavior**: The tree size is calculated dynamically in memory. Specifying `depth=1` automatically prunes lower levels, returning an empty `children` array for node 1.

### 5. Prevent Cyclic Dependencies (PATCH)
*   **HTTP Method**: `PATCH /departments/1`
*   **Payload** (trying to move parent node `1` inside its child node `2`):
    ```json
    {
      "parent_id": 2
    }
    ```
*   **Business Behavior**: The service intercepts the transaction, traces the tree graph upwards, blocks the modification, and outputs a `409 Conflict` containing `"Cyclic dependency detected"`.

### 6. Delete Department with Employee Reassignment
*   **HTTP Method**: `DELETE /departments/2?mode=reassign&reassign_to_department_id=1`
*   **Business Behavior**: Removes the "Engineering" node (`2`) but bulk-transfers Legolas directly to the "HQ Department" (`1`). Returns `204 No Content`.
*   **Alternative (`mode=cascade`)**: Running `DELETE /departments/1?mode=cascade` drops the entire node structure alongside all inner employee relations instantly.

---

## 🧪 Running Tests

The test suite runs asynchronous execution routines, applying strict database table isolation hooks (`TRUNCATE ... CASCADE`) between individual tasks to prevent side-effects.

Execute tests locally via your activated virtual environment shell:
```bash
python -m pytest
```
