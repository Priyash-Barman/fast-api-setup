---
description: Step-by-step protocol for adding a new domain feature module to the Fast Date backend
---

# Workflow: Add a New Feature Module

Follow these steps **in order**. Do not skip steps.

## Step 1: Scaffold the Module via CLI

Run the appropriate scaffolding command based on the module type:

```bash
# Standard CRUD module (list, create, edit, delete, status toggle)
poetry run create-module <singular_name> [plural_name]

# Module with file upload forms (profile images, documents, etc.)
poetry run create-form-module <singular_name> [plural_name]

# CMS module (rich text, slug-based content)
poetry run create-cms-module <singular_name> [plural_name]
```

**Example:**

```bash
poetry run create-module material materials
```

This creates `fast_app/modules/material/` with the full structure.

## Step 2: Register the Module

Open `fast_app/modules/__init__.py` and:

1. Import the new module:

```python
from fast_app.modules import material  # add here
```

2. Add to the `app_modules` list:

```python
app_modules = [
    ...
    material,  # add here
]
```

## Step 3: Register the Beanie Document Model

Open `fast_app/db/models.py` and add your new Document model to the `document_models` list — this is the **only** place Beanie registration happens.

```python
from fast_app.modules.material.models.material_model import Material

document_models = [
    ...,
    Material,  # add here
]
```

## Step 4: Define the Model (`models/<name>_model.py`)

- Extend `BaseDocument` (not `beanie.Document`)
- Always include `status`, `is_deleted`, `created_at`, `updated_at`
- Set `class Settings: name = "<plural_collection_name>"`
- Add a `@before_event(Insert, Replace)` hook for timestamps

```python
from fast_app.modules.common.models.base_model import BaseDocument

class Material(BaseDocument):
    name: str
    description: str
    status: StatusEnum = StatusEnum.ACTIVE
    is_deleted: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "materials"
```

## Step 5: Write the Schemas (`schemas/<name>_schema.py`)

Follow the Base → Create → Update → Response pattern:

```python
class MaterialBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)

class MaterialCreate(MaterialBase):
    pass

class MaterialUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    status: Optional[StatusEnum] = None

class MaterialResponse(MaterialBase):
    id: str = Field(..., alias="_id")
    status: StatusEnum
    created_at: datetime
    updated_at: datetime
```

> [!IMPORTANT]
> Every field in the Response schema that is **not guaranteed to be present in every DB document** (e.g. optional business fields, product lists, file paths) **must** have a default value:
> ```python
> products: List[str] = Field(default_factory=list)  # NOT `products: List[str]`
> business_email: Optional[str] = None               # NOT `business_email: Optional[str]`
> ```
> Missing defaults cause a `500 ValidationError` when serialising older or partial DB documents.

## Step 6: Implement the Service Layer (`services/<name>_service.py`)

Write all business logic here. Route handlers **must not** contain DB queries.

- All async functions
- Return `dict` or `model.model_dump(by_alias=True, mode="json")`
- Check `is_deleted == False` on every read
- Use `BaseDocument.aggregate_with_pagination()` for paginated lists

**File upload pattern** (avoids `NameError` on missing uploads):

```python
async def create_item(data: ItemCreateForm):
    image_path = ""  # always initialise BEFORE the conditional
    if data.profile_image:
        result = await upload_files([data.profile_image], "images")
        image_path = result[0].get("path", "")

    item = Item(image=image_path, ...)  # safe — image_path always defined
```

> [!CAUTION]
> Never reference a variable that is only defined inside an `if` block outside of it. This is the #1 cause of `500 NameError` on create/update endpoints.

## Step 7: Write the Admin API Routes (`routes/manage_<name>_api.py`)

- `@router.get|post|patch|delete(...)`
- `@catch_error` on every route (no exceptions)
- `@login_required(UserRole.ADMIN)` on every protected route
- For RBAC-gated actions, add `@action_type(Action.X)` and set `router.__resource__ = Resource.X`
- Use paginated list responses with `SuccessDataPaginated` + `PaginatedData` + `PaginationMeta`
- Use `SuccessData` for single-item responses and `SuccessResponse` for message-only
- Prefix: `/api/v1/admin/<plural>` → file: `manage_<name>_api.py`
- Thin handlers: call service → return response schema

## Step 7b: (Optional) Write End-User API Routes (`routes/my_<name>_api.py`)

For routes consumed by end-users (mobile app, etc.) that operate on the current user's own data:

- Prefix: `/api/v1/my-<plural>` → file: `my_<name>_api.py`
- `@login_required()` (no role restriction — any authenticated user)
- Read current user from `request.state.user`
- Filter service calls by `user.id` (never expose other users' data)

## Step 8: (Optional) Write Web Routes (`routes/<name>_web.py`)

For admin CRUD UIs:

- Use `ChoiceLoader` with `admin_layout.html` + module templates
- `GET /admin/<plural>/` → list template
- `GET /admin/<plural>/create` → form template
- `POST /admin/<plural>/create` → process + redirect
- `GET /admin/<plural>/{id}/edit` → form template
- `POST /admin/<plural>/{id}/edit` → process + redirect
- `GET /admin/<plural>/{id}/delete` → delete + redirect

## Step 9: Write Templates (`templates/*.html`)

```html
{% extends "admin_layout.html" %} {% block title %}Materials{% endblock %} {%
block content %}
<h4 class="manage-heading">Manage Materials</h4>
... {% endblock %}
```

**Admin template conventions:**

1. **Never render user-specific links outside `{% if user %}`** — links like `href="/admin/items/{{ item._id }}/edit"` on a *create* form will produce double-slash URLs (`/admin/items//edit`). Always guard them:
   ```html
   {% if item %}
   <a href="/admin/items/{{ item._id }}/edit">Edit</a>
   {% endif %}
   ```

2. **Never use JavaScript template literals (backticks) in Jinja2 templates** — Jinja2 tries to interpolate `${...}` and may conflict. Always use string concatenation:
   ```js
   // WRONG:
   $.ajax({ url: `/api/v1/items/${itemId}` })
   // CORRECT:
   $.ajax({ url: '/api/v1/items/' + itemId })
   ```

3. **Error toasts must parse both `message` and `detail`** — FastAPI returns `detail` for `HTTPException`, the app returns `message` in `ErrorResponse`. Always check both:
   ```js
   error: function (xhr) {
       const resp = xhr.responseJSON;
       const msg = resp ? (resp.message || resp.detail || 'Action failed') : 'Action failed';
       toastr.error(msg);
   }
   ```

4. **Use data attributes for dynamic button actions** instead of inline `onclick` with Jinja values — avoids syntax errors when values contain quotes or special characters:
   ```html
   <!-- CORRECT -->
   <button class="delete-btn" data-id="{{ item._id }}">Delete</button>
   <script>
   $('.delete-btn').on('click', function() { const id = $(this).data('id'); ... });
   </script>
   ```

5. **Sidebar active state** — use `.rstrip('/')` to normalize trailing slashes:
   ```html
   <a href="/admin" class="{{ 'active' if request.url.path.rstrip('/') == '/admin' else '' }}">Dashboard</a>
   ```
   For sub-paths use `in`:
   ```html
   <a class="{{ 'active' if '/admin/materials' in request.url.path else '' }}">
   ```

## Step 10: Register in `__init__.py` (module-level)

Open `modules/<name>/__init__.py` and include all routers:

```python
from fastapi import FastAPI
from fast_app.modules.material.routes import manage_material_api, material_web
# from fast_app.modules.material.routes import my_material_api  # if user-facing routes exist

def register_routes(app: FastAPI):
    app.include_router(manage_material_api.router, tags=["Admin Materials"])
    app.include_router(material_web.router, tags=["Materials Web"])
    # app.include_router(my_material_api.router, tags=["My Materials"])
```

> [!NOTE]
> Do **not** add a global prefix here — each router already carries its own full prefix (e.g., `/api/v1/admin/materials`).

## Step 11: Verify

```bash
poetry run dev
```

- Browse to `http://localhost:<PORT>/apidoc/v1` and verify the new endpoints appear.
- Test GET list, POST create, PATCH update, DELETE (soft) manually or via the Swagger UI.
