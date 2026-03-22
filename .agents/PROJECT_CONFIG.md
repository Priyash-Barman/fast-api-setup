# ⚙️ PROJECT_CONFIG.md — Code of Conduct

> **Fast Date**

---

## 📛 Naming Conventions

| Entity             | Convention            | Example                                              |
| ------------------ | --------------------- | ---------------------------------------------------- |
| Modules            | `snake_case`          | `contact_us`, `privacy_policy`                       |
| Model classes      | `PascalCase`          | `Demo`, `UserDevice`, `Product`                      |
| Schema classes     | `PascalCase` + suffix | `DemoCreate`, `DemoUpdate`, `DemoResponse`           |
| Service functions  | `snake_case` verbs    | `get_demo_by_id`, `create_demo`, `remove_demo`       |
| Route functions    | `snake_case` verbs    | `list_demos`, `create_form`, `toggle_demo_status`    |
| Enum classes       | `PascalCase`          | `StatusEnum`, `UserRole`, `OtpPurpose`               |
| Enum values        | `UPPER_SNAKE_CASE`    | `StatusEnum.ACTIVE`, `UserRole.END_USER`             |
| Files              | `snake_case` + suffix | `demo_model.py`, `demo_schema.py`, `demo_service.py` |
| HTML templates     | `snake_case.html`     | `list.html`, `form.html`, `login.html`               |
| MongoDB collection | `snake_case` plural   | `demos`, `user_devices`, `products`                  |

---

## 🗂️ Module Internal Structure

Every module **must** follow this exact folder structure (enforced by CLI scaffolding):

```
modules/<module_name>/
├── __init__.py          # register_routes(app) function — MANDATORY
├── models/
│   └── <name>_model.py  # Beanie Document subclass
├── schemas/
│   └── <name>_schema.py # Pydantic v2 Create/Update/Response schemas
├── services/
│   └── <name>_service.py # All business logic — NO DB access in routes
├── routes/
│   ├── <name>_api.py    # JSON API routes
│   └── <name>_web.py    # (Optional) Jinja2 template web routes
└── templates/           # (Optional) Jinja2 HTML files
    └── *.html
```

> [!IMPORTANT]
> The `__init__.py` **must** expose a `register_routes(app)` function that includes all sub-routers. This is how `register_all_routes` discovers and mounts module routes.

---

## 🌐 API Routes

### Required Decorator Stack

Every API route **must** apply decorators in this exact order:

```python
@router.get("/path")
@catch_error                              # ALWAYS — first after HTTP method
@login_required(UserRole.ADMIN)          # Only if authentication required
async def handler(request: Request):
    ...
```

> [!CAUTION]
> **Never** omit `@catch_error`. Routes without it will crash with unformatted 500 errors that bypass the `ErrorResponse` schema.

### Response Models

All API routes **must** use one of these centralized response models:

```python
from fast_app.modules.common.schemas.response_schema import (
    SuccessResponse,       # Message-only success: { status, message }
    SuccessData,           # Success with data: { status, message, data }
    SuccessDataPaginated,  # Paginated list: { status, message, data: { meta, docs } }
    PaginatedData,         # Pagination wrapper: { meta: PaginationMeta, docs: [...] }
    PaginationMeta,        # Pagination metadata: total_docs, page, limit, has_next, etc.
)
```

Always return with the response model declared:

```python
# Simple data response
@router.get("/", response_model=SuccessData)
async def list_items(request: Request):
    data = await my_service.get_items()
    return SuccessData(message="Items fetched.", data=data)

# Paginated response
@router.get("/", response_model=SuccessDataPaginated[MyResponseSchema])
async def list_items_paged(request: Request, page: int = Query(1, ge=1), limit: int = Query(10)):
    docs, pagination = await my_service.get_paginated(page=page, limit=limit)
    return SuccessDataPaginated(
        message="Items fetched.",
        data=PaginatedData(meta=PaginationMeta(**pagination), docs=docs),
    )
```

### Router Prefix Convention

| Route type           | Prefix                        | Example                             | File                         |
| -------------------- | ----------------------------- | ----------------------------------- | ---------------------------- |
| Admin API            | `/api/v1/admin/<plural>`      | `/api/v1/admin/notifications`       | `manage_*_api.py`            |
| User Auth API        | `/api/v1/auth/user`           | `/api/v1/auth/user/send-otp`        | `user_auth_api.py`           |
| Admin Auth API       | `/api/v1/auth`                | `/api/v1/auth/admin/login`          | `admin_auth_api.py`          |
| End-User API (mine)  | `/api/v1/my-<plural>`         | `/api/v1/my-notifications`          | `my_*_api.py`                |
| Web (UI) routes      | `/admin/<plural>`             | `/admin/demos`                      | `*_web.py`                   |

---

## 🗄️ Models (Beanie ODM)

### BaseDocument

All Document models **must** extend `BaseDocument`, not `beanie.Document` directly:

```python
from fast_app.modules.common.models.base_model import BaseDocument

class Product(BaseDocument):
    name: str
    status: StatusEnum = StatusEnum.ACTIVE
    is_deleted: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "products"  # MongoDB collection name — always plural snake_case
```

> [!IMPORTANT]
> After creating a model class, **always add it** to `fast_app/db/models.py` → `document_models` list. This is the only place Beanie document registration happens.

### Mandatory Fields

| Field        | Type         | Default             | Rule                                    |
| ------------ | ------------ | ------------------- | --------------------------------------- |
| `status`     | `StatusEnum` | `StatusEnum.ACTIVE` | Always present                          |
| `is_deleted` | `bool`       | `False`             | Soft-delete pattern — never hard-delete |
| `created_at` | `datetime`   | `datetime.utcnow`   | Managed by `before_event` hook          |
| `updated_at` | `datetime`   | `datetime.utcnow`   | Managed by `before_event` hook          |

### Timestamp Hook

Timestamps **must** be managed via Beanie's `@before_event` hooks:

```python
from beanie import Insert, Replace, before_event

@before_event(Insert, Replace)
def set_timestamps(self):
    if not self.created_at:
        self.created_at = datetime.utcnow()
    self.updated_at = datetime.utcnow()
```

### Query Conventions

- Always filter `is_deleted == False` on read operations.
- Use `await Model.find_one(...)` for single document lookups.
- Use `BaseDocument.aggregate_with_pagination(pipeline, page, limit)` for paginated list views.
- Use `BaseDocument.aggregate_list(pipeline)` for non-paginated list views.
- Serialization: `document.model_dump(by_alias=True, mode="json")` before returning to a route.

---

## 📐 Schemas (Pydantic v2)

### Schema Hierarchy Pattern

```python
class DemoBase(BaseModel):              # Shared fields with validators
    name: str = Field(..., min_length=2, max_length=100)

class DemoCreate(DemoBase):             # POST body — all required
    pass

class DemoUpdate(BaseModel):            # PATCH body — all Optional
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    status: Optional[StatusEnum] = None

class DemoResponse(DemoBase):           # Response shape
    id: str = Field(..., alias="_id")
    status: StatusEnum
    created_at: datetime
    updated_at: datetime
```

> [!IMPORTANT]
> `Update` schemas **must** have all fields as `Optional`. Never reuse a `Create` schema as an `Update` schema.

### Form Schemas (File Uploads)

When a route accepts multipart forms with file uploads, use the `as_form` classmethod pattern (see `AdminProfileUpdateForm` in `admin_auth_schema.py`).

---

## 🔐 Authentication & Authorization

### `@login_required` Rules

```python
# Single role:
@login_required(UserRole.ADMIN)

# Multiple roles:
@login_required(UserRole.ADMIN, UserRole.SUPER_ADMIN)

# Any authenticated user:
@login_required()
```

After the decorator runs, the authenticated user is available on `request.state.user` and the token on `request.state.access_token`.

### RBAC — Resource & Action Permissions (Admin routes)

Admin routes that are gated by fine-grained permissions **must** also declare a `Resource` via `__resource__` on the router and (optionally) an `Action` via `@action_type`:

```python
from fast_app.decorators.permission_decorator import action_type
from fast_app.defaults.permission_enums import Resource, Action

# On the router:
router = APIRouter(prefix="/api/v1/admin/users")
router.__resource__ = Resource.USER  # type: ignore[attr-defined]

# On individual routes that need action-level control:
@router.delete("/{id}")
@catch_error
@login_required(UserRole.ADMIN)
@action_type(Action.DELETE)
async def delete_user(request: Request, id: str):
    ...
```

The RBAC check in `utils/auth_utils.py` → `check_access()` automatically resolves whether the admin has the required `Resource` + `Action` in their `user.permissions` map. `SUPER_ADMIN` bypasses all RBAC checks.

### Password Hashing

Always use `utils/crypto_utils.py`:

```python
from fast_app.utils.crypto_utils import hash_password
hashed = hash_password(plain_password)
```

Never use `hashlib`, `bcrypt`, or any other library directly.

### JWT Utilities

Use `utils/jwt_utils.py` exclusively:

```python
from fast_app.utils.jwt_utils import create_access_token, create_refresh_token
access_token = create_access_token({"sub": str(user.id)})
refresh_token = create_refresh_token(str(user.id))
```

---

## 🖼️ Templating (Jinja2 / Web Routes)

All web routes **must** configure templates using the `ChoiceLoader` pattern:

```python
from jinja2 import ChoiceLoader, FileSystemLoader
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="fast_app/modules/<module>/templates")
templates.env.loader = ChoiceLoader([
    FileSystemLoader("fast_app/modules/common/templates/layouts"),
    FileSystemLoader("fast_app/modules/<module>/templates"),
])
```

All templates **must** extend `admin_layout.html` and define `{% block title %}` and `{% block content %}`:

```html
{% extends "admin_layout.html" %} {% block title %}Page Title{% endblock %} {%
block content %} ... {% endblock %}
```

---

## 🚫 Anti-Patterns

> [!WARNING]
> Violating these rules will be rejected in code review.

| ❌ Anti-Pattern                                               | ✅ Correct Approach                                             |
| ------------------------------------------------------------- | --------------------------------------------------------------- |
| Raw `try/except` inside a route handler                       | Use `@catch_error` decorator                                    |
| Querying DB directly in a route handler                       | Call a service function                                         |
| Importing `motor` directly in app logic                       | Use Beanie ODM methods                                          |
| Hard-deleting documents                                       | Set `is_deleted = True`                                         |
| Using `any` type annotation                                   | Annotate explicitly; use `Dict[str, Any]` if dynamic            |
| `datetime.now()` (timezone-naive)                             | `datetime.utcnow()` everywhere                                  |
| Defining shared enums inside a module                         | Put them in `defaults/*.py`                                     |
| Inline styles in Jinja templates                              | Bootstrap 5 utility classes only                                |
| Creating modules by hand                                      | Use `poetry run create-module <name>`                           |
| Direct `boto3` S3 calls in routes/services                    | Use `utils/file_utils.py`                                       |
| Returning `model_dump()` without `by_alias=True, mode="json"` | Always use both flags                                           |
| Naked `except:` clause                                        | `except HTTPException` then `except Exception`                  |
| Adding model to `init_beanie` inline in lifespan              | Add to `fast_app/db/models.py` → `document_models` list        |
| Admin RBAC route without `@action_type` or `__resource__`     | Decorate with `@action_type(Action.X)` and set router resource  |
| Returning paginated data as plain `SuccessData`               | Use `SuccessDataPaginated` + `PaginatedData` + `PaginationMeta` |

---

## 🛠️ CLI Commands

```bash
# Scaffold a new standard CRUD module
poetry run create-module <singular> [plural]

# Scaffold a new form-based module (with file upload support)
poetry run create-form-module <singular> [plural]

# Scaffold a CMS module (rich-text content management)
poetry run create-cms-module <singular> [plural]
```

After scaffolding, manually:

1. Add the new module to `modules/__init__.py` → `app_modules` list.
2. Register your Beanie document model in `db/mongodb.py` or the lifespan initializer.

---

## 🚀 Running the Project

```bash
# Development (hot reload)
poetry run dev

# Production
poetry run start
```

API docs available at: `http://localhost:<PORT>/apidoc/v1`
