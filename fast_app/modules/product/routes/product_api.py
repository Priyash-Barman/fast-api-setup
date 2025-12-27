from fastapi import APIRouter, File, Form, HTTPException, Query, UploadFile, status, Request
from typing import Optional

from fast_app.decorators.authenticator import login_required
from fast_app.modules.product.services import product_service
from fast_app.decorators.catch_error import catch_error
from fast_app.defaults.common_enums import StatusEnum, UserRole

from fast_app.modules.product.schemas.product_schema import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
)

from fast_app.modules.common.schemas.response_schema import (
    PaginatedData,
    PaginationMeta,
    SuccessResponse,
    PaginationData,
    SuccessData,
    SuccessDataPaginated,
)

router = APIRouter(prefix="/products")


@router.get("/", response_model=SuccessDataPaginated[ProductResponse])
@catch_error
@login_required(UserRole.ADMIN)
async def list_products(
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

    products, pagination = await product_service.get_products(
        page=page,
        limit=limit,
        search=search,
        sort=sort,
        filters=filters,
    )

    return SuccessDataPaginated(
        message="Products retrieved successfully",
        data=PaginatedData(
            meta=PaginationMeta(**pagination),
            docs=products,
        ),
    )



@router.get("/{product_id}", response_model=SuccessData[dict])
@catch_error
@login_required(UserRole.ADMIN)
async def get_product(request: Request, product_id: str):

    product = await product_service.get_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return SuccessData(message="Product retrieved successfully", data=product)


@router.post("/", response_model=SuccessData[dict], status_code=status.HTTP_201_CREATED)
@catch_error
@login_required(UserRole.ADMIN)
async def create_product(
    request: Request,
    name: str = Form(...),
    image: UploadFile = File(...)
):

    product = await product_service.create_product(ProductCreate(name=name,image=image))
    return SuccessData(message="Product created successfully", data=product)


@router.put("/{product_id}", response_model=SuccessData[dict])
@catch_error
@login_required(UserRole.ADMIN)
async def update_product(
    request: Request,
    product_id: str,
    name: str = Form(...),
    image: UploadFile = File(...)
):

    product = await product_service.update_product(product_id, ProductUpdate(name=name, image=image))
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return SuccessData(message="Product updated successfully", data=product)


@router.patch("/{product_id}/status", response_model=SuccessData[dict])
@catch_error
@login_required(UserRole.ADMIN)
async def update_status(
    request: Request,
    product_id: str,
    status_data: StatusEnum,
):
    product = await product_service.change_product_status(product_id, status_data)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return SuccessData(message="Product status updated successfully", data=product)


@router.delete("/{product_id}", response_model=SuccessResponse)
@catch_error
@login_required(UserRole.ADMIN)
async def delete_product(request: Request, product_id: str):

    if not await product_service.remove_product(product_id):
        raise HTTPException(status_code=404, detail="Product not found")

    return SuccessResponse(message="Product deleted successfully")
