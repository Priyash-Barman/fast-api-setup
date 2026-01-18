from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status, Request
from typing import Optional

from fast_app.core.router_context import RouterContext
from fast_app.decorators.authenticator import login_required
from fast_app.decorators.permission_decorator import action_type
from fast_app.defaults.permission_enums import Action, Resource
from fast_app.modules.category.services import category_service
from fast_app.decorators.catch_error import catch_error
from fast_app.defaults.common_enums import StatusEnum, UserRole

from fast_app.modules.category.schemas.category_schema import (
    CategoryCreateForm,
    CategoryResponse,
    CategoryStatusUpdateSchema,
    CategoryUpdateForm,
)

from fast_app.modules.common.schemas.response_schema import (
    PaginatedData,
    PaginationMeta,
    SuccessResponse,
    SuccessData,
    SuccessDataPaginated,
)

router = RouterContext(prefix="/categories", name=Resource.CATEGORY)


@router.get("", response_model=SuccessDataPaginated[CategoryResponse])
@catch_error
@login_required(UserRole.ADMIN)
@action_type(Action.READ)
async def list_categories(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    sort: Optional[str] = Query(None),
    status_filter: Optional[StatusEnum] = Query(None),
):
    filters = {}
    if status_filter:
        filters["status"] = status_filter

    categories, pagination = await category_service.get_categories(
        page=page,
        limit=limit,
        search=search,
        sort=sort,
        filters=filters,
    )

    return SuccessDataPaginated(
        message="Categories retrieved successfully",
        data=PaginatedData(
            meta=PaginationMeta(**pagination),
            docs=categories,
        ),
    )



@router.get("/{category_id}", response_model=SuccessData[dict])
@catch_error
@login_required(UserRole.ADMIN)
@action_type(Action.READ)
async def get_category(request: Request, category_id: str):

    category = await category_service.get_category_by_id(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    return SuccessData(message="Category retrieved successfully", data=category)


@router.post("", response_model=SuccessData[dict], status_code=status.HTTP_201_CREATED)
@catch_error
@login_required(UserRole.ADMIN)
@action_type(Action.CREATE)
async def create_category(
    request: Request,
    form: CategoryCreateForm = Depends(CategoryCreateForm.as_form)
):

    category = await category_service.create_category(form)
    return SuccessData(message="Category created successfully", data=category)


@router.put("/{category_id}", response_model=SuccessData[dict])
@catch_error
@login_required(UserRole.ADMIN)
@action_type(Action.UPDATE)
async def update_category(
    request: Request,
    category_id: str,
    form: CategoryUpdateForm = Depends(CategoryUpdateForm.as_form),
):
    category = await category_service.update_category(category_id, form)

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    return SuccessData(
        message="Category updated successfully",
        data=category
    )


@router.patch("/{category_id}/status", response_model=SuccessData[dict])
@catch_error
@login_required(UserRole.ADMIN)
@action_type(Action.UPDATE)
async def update_status(
    request: Request,
    category_id: str,
    data: CategoryStatusUpdateSchema
):
    category = await category_service.change_category_status(category_id, data.status)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    return SuccessData(message="Category status updated successfully", data=category)


@router.delete("/{category_id}", response_model=SuccessResponse)
@catch_error
@login_required(UserRole.ADMIN)
@action_type(Action.DELETE)
async def delete_category(request: Request, category_id: str):

    if not await category_service.remove_category(category_id):
        raise HTTPException(status_code=404, detail="Category not found")

    return SuccessResponse(message="Category deleted successfully")
