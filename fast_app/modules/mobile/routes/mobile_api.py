from fastapi import APIRouter, HTTPException, Query, status, Request
from typing import Optional

from fast_app.modules.mobile.services import mobile_service
from fast_app.decorators.catch_error import catch_error
from fast_app.defaults.common_enums import StatusEnum

from fast_app.modules.mobile.schemas.mobile_schema import (
    MobileCreate,
    MobileUpdate,
    MobileResponse,
)

from fast_app.modules.common.schemas.response_schema import (
    PaginatedData,
    PaginationMeta,
    SuccessResponse,
    PaginationData,
    SuccessData,
    SuccessDataPaginated,
)

router = APIRouter(prefix="/mobiles")


@router.get("/", response_model=SuccessDataPaginated[MobileResponse])
@catch_error
async def list_mobiles(
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

    mobiles, pagination = await mobile_service.get_mobiles(
        page=page,
        limit=limit,
        search=search,
        sort=sort,
        filters=filters,
    )

    return SuccessDataPaginated(
        message="Mobiles retrieved successfully",
        data=PaginatedData(
            meta=PaginationMeta(**pagination),
            docs=mobiles,
        ),
    )



@router.get("/{mobile_id}", response_model=SuccessData[dict])
@catch_error
async def get_mobile(request: Request, mobile_id: str):

    mobile = await mobile_service.get_mobile_by_id(mobile_id)
    if not mobile:
        raise HTTPException(status_code=404, detail="Mobile not found")

    return SuccessData(message="Mobile retrieved successfully", data=mobile)


@router.post("/", response_model=SuccessData[dict], status_code=status.HTTP_201_CREATED)
@catch_error
async def create_mobile(request: Request, mobile_data: MobileCreate):

    mobile = await mobile_service.create_mobile(mobile_data)
    return SuccessData(message="Mobile created successfully", data=mobile)


@router.put("/{mobile_id}", response_model=SuccessData[dict])
@catch_error
async def update_mobile(request: Request, mobile_id: str, mobile_data: MobileUpdate):

    mobile = await mobile_service.update_mobile(mobile_id, mobile_data)
    if not mobile:
        raise HTTPException(status_code=404, detail="Mobile not found")

    return SuccessData(message="Mobile updated successfully", data=mobile)


@router.patch("/{mobile_id}/status", response_model=SuccessData[dict])
@catch_error
async def update_status(
    request: Request,
    mobile_id: str,
    status_data: StatusEnum,
):
    mobile = await mobile_service.change_mobile_status(mobile_id, status_data)
    if not mobile:
        raise HTTPException(status_code=404, detail="Mobile not found")

    return SuccessData(message="Mobile status updated successfully", data=mobile)


@router.delete("/{mobile_id}", response_model=SuccessResponse)
@catch_error
async def delete_mobile(request: Request, mobile_id: str):

    if not await mobile_service.remove_mobile(mobile_id):
        raise HTTPException(status_code=404, detail="Mobile not found")

    return SuccessResponse(message="Mobile deleted successfully")
