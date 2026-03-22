---
description: Standard protocol for tracing and resolving bugs across the Fast Date FastAPI backend stack
---

# Workflow: Debug Standard

Follow this triage protocol in order when encountering a bug or unexpected behavior.

---

## Phase 1: Classify the Error

Identify the **error surface** first:

| Symptom                                 | Error Surface                                                         |
| --------------------------------------- | --------------------------------------------------------------------- |
| `422 Unprocessable Entity`              | Pydantic schema validation failure                                    |
| `500 Internal Server Error`             | Unhandled exception in service or missing `@catch_error`              |
| `401 Unauthorized`                      | JWT missing/expired, or `@login_required` misconfigured               |
| `403 Forbidden`                         | Wrong `UserRole` in `@login_required`, RBAC denied, or **missing `Authorization` header** in AJAX request |
| `404 Not Found`                         | Service returned `None`, route params wrong, module not registered, or **double-slash URL from orphaned Jinja template link** |
| Template renders blank / missing layout | `ChoiceLoader` misconfigured, base template path wrong                |
| Route not appearing in `/apidoc/v1`     | Module not in `app_modules`, `register_routes` not called             |

---

## Phase 2: Trace the Error

### 2A — API Errors (JSON endpoints)

1. **Check the terminal output** — `@catch_error` always calls `traceback.print_exc()`. The full traceback will appear in the server console.

2. **Check the response body** — all errors return `ErrorResponse` shape:

   ```json
   { "status": "error", "message": "..." }
   ```

   The `message` field is your clue.

3. **Locate the route handler** in `routes/<name>_api.py`. Confirm:
   - `@catch_error` is present
   - `@login_required` roles are correct
   - Schema parameter types match the request body

4. **Locate the service function** it calls. Look for:
   - Missing `is_deleted == False` filter
   - Wrong Beanie query (`.find_one()` vs `.find()`)
   - Missing `await` on async calls
   - `model_dump()` called without `by_alias=True, mode="json"`

5. **Check the Pydantic schema** if `422`:
   - Field validators match the input format
   - Optional fields are correctly typed `Optional[X] = None`
   - Enum values match what the client is sending

### 2B — Auth Errors (`401` / `403`)

1. Confirm the route has `@login_required` with the correct roles.
2. Check `utils/auth_utils.py` → `check_access()` for RBAC logic.
3. **Verify the `Authorization: Bearer <token>` header is present in the AJAX request.** In the admin panel, the global `$.ajaxSetup` in `admin_layout.html` should attach the token from `localStorage.getItem('admin_token')` automatically. If it's missing, this is the primary cause of `403` on POST/PATCH/DELETE calls.
4. If token appears valid but fails: check if the `UserDevice` session has `expired = True`.
5. Check `utils/jwt_utils.py` for token expiry times.
6. For `403` on an admin route: check if the router has `router.__resource__` set and if the admin's `user.permissions` map includes that `Resource`. Also check if the route `@action_type` requires an action the admin doesn't have.
7. **`SUPER_ADMIN` bypass**: `SUPER_ADMIN` role must pass all role checks that include `UserRole.ADMIN`. Confirm `check_access()` handles this — if `user.role == UserRole.SUPER_ADMIN` and the required roles contain `ADMIN`, it must return early without checking granular permissions.

### 2C — Database / Beanie Errors

1. Check that the Beanie Document model is registered in the `init_beanie` call in the DB setup.
2. Verify `class Settings: name = "<collection>"` is correct collection name.
3. Check that aggregation pipelines use valid MongoDB operators.
4. For `_id` field issues: ensure `Field(..., alias="_id")` in the Response schema and `by_alias=True` in `model_dump()`.

### 2D — Template / Web Route Errors

1. Verify the `ChoiceLoader` paths are correct:
   ```python
   FileSystemLoader("fast_app/modules/common/templates/layouts"),
   FileSystemLoader("fast_app/modules/<name>/templates"),
   ```
2. Verify the template extends `admin_layout.html`.
3. Confirm the template file name matches what `TemplateResponse` calls.
4. If form data is missing: check `Form(...)` parameter types in the route handler.

### 2E — Route Not Found / Not Registered

1. Check `modules/__init__.py` → `app_modules` list includes the module.
2. Check the module's `__init__.py` → `register_routes` includes the router.
3. Check the router's `prefix` — ensure no double-slashes or typos.
4. Confirm the module's `__init__.py` does NOT import from modules that haven't been registered yet (circular import risk).
5. **Double-slash URLs (`/admin/users//permissions`)**: Caused by Jinja2 links like `href="/admin/users/{{ user._id }}/permissions"` rendered when `user` is `None` (e.g., on a create form). Always guard such links with `{% if user %}...{% endif %}`.

### 2F — Internal Server Errors in Service (`500`)

1. **Uninitialised variable before conditional upload**: A common pattern is:
   ```python
   if user_data.profile_image:
       upload_result = await upload_files(...)
       image_data = upload_result[0]  # ← only defined when image exists

   user = User(profile_image=image_data.get("path", ""))  # ← NameError when no image!
   ```
   **Fix**: Initialise `image_path = ""` before the `if` block, then assign inside it.

2. **Response schema missing `Optional` defaults**: If a Pydantic response schema has non-optional fields (e.g. `products: List[str]`) that are absent in the DB document, serialisation raises a `ValidationError` which becomes a `500`. Always ensure all fields not guaranteed to exist in the document are `Optional[X] = None` or `List[X] = Field(default_factory=list)`.

---

## Phase 3: Fix

Apply the fix at the **lowest level** where the bug exists:

- Schema bug → `schemas/<name>_schema.py`
- Logic bug → `services/<name>_service.py`
- Route configuration bug → `routes/<name>_api.py`
- Auth bug → `decorators/authenticator.py` or `utils/auth_utils.py`
- Template bug → `templates/*.html` or web route loader config

> [!TIP]
> Never fix a service bug by patching the route handler. Fix it at the source.

---

## Phase 4: Verify

```bash
# Restart dev server to pick up changes
poetry run dev
```

1. Re-run the failing request (via Swagger UI at `/apidoc/v1` or the browser).
2. Confirm the terminal no longer prints the error traceback.
3. Confirm the response matches the expected `SuccessData` or `SuccessResponse` shape.

---

## Phase 5: Prevent Regression

- If the bug was a missing `@catch_error`: audit **all** routes in the affected module.
- If the bug was a missing `is_deleted == False` filter: audit **all** `find_one` queries in the service.
- If the bug was a Pydantic schema mismatch: check if the same schema is reused in other routes that may be affected.

---

## Quick Reference: Common Fixes

| Error                                    | Root Cause                           | Fix                                    |
| ---------------------------------------- | ------------------------------------ | -------------------------------------- |
| `500` + blank message                    | Missing `@catch_error`               | Add decorator to route                 |
| `500` + `NameError`                      | Variable only defined inside `if` block | Initialise with default before the block |
| `500` on user creation/response          | Response schema has required field missing in DB doc | Add `= None` or `Field(default_factory=...)` to schema |
| `422` on valid input                     | Schema type mismatch                 | Make field `Optional` or fix validator |
| `401` on valid token                     | Token expired in DB                  | Use refresh token or re-login          |
| `403` from admin panel AJAX              | Missing `Authorization` header       | Ensure `$.ajaxSetup` in layout sets Bearer token globally |
| `403` on admin route                     | RBAC `Resource`/`Action` denied      | Check admin permissions or add `@action_type` |
| `403` for `SUPER_ADMIN`                  | `check_access` doesn't bypass correctly | Confirm `SUPER_ADMIN` returns early before permission checks |
| Empty list returned                      | Missing `is_deleted == False` filter | Add filter to Beanie query             |
| `AttributeError` on `request.state.user` | `@login_required` not applied        | Add decorator                          |
| Serialization `_id` missing              | `by_alias=False` in `model_dump`     | Add `by_alias=True, mode="json"`       |
| Template `TemplateNotFound`              | Loader path wrong                    | Fix `FileSystemLoader` paths           |
| Route missing from docs                  | Module not in `app_modules`          | Add to `modules/__init__.py`           |
| Double-slash URL `/resource//action`     | Jinja link rendered with `None` ID  | Wrap link in `{% if user %}...{% endif %}` |
| Toast shows generic error, not detail    | `xhr.responseJSON.detail` is `undefined` | Parse as `resp.message \|\| resp.detail \|\| fallback` |
| Sidebar active state not highlighting    | Exact path match fails on trailing slash | Use `.rstrip('/')` before comparing `request.url.path` |
