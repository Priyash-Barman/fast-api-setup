from fastapi import APIRouter, Request, Form, Query, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Any, Dict, Optional

from fast_app.modules.user.services import user_service
from fast_app.modules.user.schemas.user_schema import (
    UserCreate,
    UserUpdate,
)
from fast_app.defaults.enums import UserRole
from fast_app.decorators.catch_error import catch_error

from jinja2 import ChoiceLoader, FileSystemLoader

router = APIRouter(prefix="/admin/users")

# Template loaders
templates = Jinja2Templates(directory="modules/user/templates")
templates.env.loader = ChoiceLoader([
    FileSystemLoader("fast_app/modules/common/templates/layouts"),
    FileSystemLoader("fast_app/modules/user/templates"),
])


# ----------------------------
# LIST USERS (Admin HTML Page)
# ----------------------------
@router.get("/", name="admin_users:list")
@catch_error
async def list_users(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    sort: Optional[str] = Query(None),
    is_active: Optional[str] = Query(None),
    role: Optional[str] = Query(None),
):
    filters: Dict[str, Any] = {}

    if is_active and is_active.lower() != "null":
        filters["is_active"] = is_active.lower() == "true"

    if role and role.lower() != "null":
        filters["role"] = role.lower()

    users, pagination = await user_service.get_users(
        page=page, limit=limit, search=search, sort=sort, filters=filters
    )
        
    return templates.TemplateResponse("list.html", {
        "request": request,
        "users": users,
        "search": search,
        "sort": sort,
        "is_active": is_active if is_active != "null" else None,
        "role": role if role != "null" else None,
        "pagination": pagination,
    })


# ----------------------------
# CREATE USER (FORM)
# ----------------------------
@router.get("/create", name="admin_users:create_form")
@catch_error
async def create_user_form(request: Request):
    return templates.TemplateResponse("form.html", {
        "request": request,
        "user": None,
        "form_action": "/admin/users/create",
        "form_method": "POST",
    })


@router.post("/create", name="admin_users:create")
@catch_error
async def create_user(
    request: Request,
    full_name: str = Form(...),
    email: str = Form(...),
):
    user_data = UserCreate(
        full_name=full_name,
        email=email,
        role=UserRole.ADMIN  # or END_USER as per requirement
    )

    try:
        await user_service.create_new_user(user_data)
    except ValueError:
        return RedirectResponse(url="/admin/users/create", status_code=status.HTTP_302_FOUND)

    return RedirectResponse(url="/admin/users", status_code=status.HTTP_302_FOUND)


# ----------------------------
# EDIT USER (FORM)
# ----------------------------
@router.get("/{user_id}/edit", name="admin_users:edit_form")
@catch_error
async def edit_user_form(request: Request, user_id: str):
    user = await user_service.get_user_by_id(user_id)
    if not user:
        return RedirectResponse(url="/admin/users", status_code=status.HTTP_302_FOUND)

    return templates.TemplateResponse("form.html", {
        "request": request,
        "user": user,
        "form_action": f"/admin/users/{user_id}/edit",
        "form_method": "POST",
    })


@router.post("/{user_id}/edit", name="admin_users:update")
@catch_error
async def update_user(
    request: Request,
    user_id: str,
    full_name: str = Form(...),
    email: str = Form(...),
):
    user_data = UserUpdate(full_name=full_name, email=email)

    await user_service.update_user_details(user_id, user_data)

    return RedirectResponse(url="/admin/users", status_code=status.HTTP_302_FOUND)


# ----------------------------
# DELETE USER
# ----------------------------
@router.get("/{user_id}/delete", name="admin_users:delete")
@catch_error
async def delete_user(request: Request, user_id: str):
    await user_service.remove_user(user_id)
    return RedirectResponse(url="/admin/users", status_code=status.HTTP_302_FOUND)


# ----------------------------
# TOGGLE ACTIVE/INACTIVE
# ----------------------------
@router.get("/{user_id}/toggle", name="admin_users:toggle_status")
@catch_error
async def toggle_user_status(request: Request, user_id: str):
    user = await user_service.get_user_by_id(user_id)

    if user:
        await user_service.change_user_status(user_id, not user.get('is_active'))

    return RedirectResponse(url="/admin/users", status_code=status.HTTP_302_FOUND)
