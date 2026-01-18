from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status, Request
from typing import List, Optional

from fast_app.core.router_context import RouterContext
from fast_app.decorators.authenticator import login_required
from fast_app.decorators.permission_decorator import action_type
from fast_app.defaults.permission_enums import Action, Resource
from fast_app.modules.product.services import product_service
from fast_app.decorators.catch_error import catch_error
from fast_app.defaults.common_enums import StatusEnum, UserRole

from fast_app.modules.product.schemas.product_schema import (
    ProductCreateForm,
    ProductResponse,
    ProductStatusUpdateSchema,
    ProductUpdateForm,
)

from fast_app.modules.common.schemas.response_schema import (
    PaginatedData,
    PaginationMeta,
    SuccessResponse,
    PaginationData,
    SuccessData,
    SuccessDataPaginated,
)

router = RouterContext(prefix="/user/products", name=Resource.PRODUCT)


@router.get("", response_model=SuccessDataPaginated[ProductResponse])
@catch_error
@action_type(Action.READ)
async def list_products(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    sort: Optional[str] = Query(None),
    status_filter: Optional[StatusEnum] = Query(None),
    category_filter: List[Optional[str|PydanticObjectId]] = Query(default=[], alias="category_filter[]")
):
    filters = {}
    if status_filter:
        filters["status"] = status_filter

    products, pagination = await product_service.get_products(
        page=page,
        limit=limit,
        search=search,
        sort=sort,
        filters=filters,
        category_filter=category_filter
    )

    return SuccessDataPaginated(
        message="Products retrieved successfully",
        data=PaginatedData(
            meta=PaginationMeta(**pagination),
            docs=products,
        ),
    )




@router.get("/group-category", response_model=SuccessDataPaginated[dict])
@catch_error
@action_type(Action.READ)
@login_required(UserRole.END_USER, UserRole.VENDOR)
async def list_products_group_by_category(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    status_filter: Optional[StatusEnum] = Query(None),
    category_filter: List[Optional[str|PydanticObjectId]] = Query(default=[], alias="category_filter[]")
):
    filters = {}
    if status_filter:
        filters["status"] = status_filter

    data, pagination = await product_service.get_products_group_by_category(
        page=page,
        limit=limit,
        search=search,
        filters=filters,
        category_filter=category_filter
    )

    return SuccessDataPaginated(
        message="Products retrieved successfully",
        data=PaginatedData(
            meta=PaginationMeta(**pagination),
            docs=data,
        ),
    )



@router.get("/{product_id}", response_model=SuccessData[dict])
@catch_error
@action_type(Action.READ)
async def get_product(request: Request, product_id: str):

    product = await product_service.get_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return SuccessData(message="Product retrieved successfully", data=product)

