from fastapi import APIRouter, HTTPException, Query, status, Request
from typing import Optional

from fast_app.modules.demo.services import demo_service
from fast_app.decorators.catch_error import catch_error
from fast_app.defaults.common_enums import StatusEnum

from fast_app.modules.demo.schemas.demo_schema import (
    DemoCreate,
    DemoUpdate,
    DemoResponse,
)

from fast_app.modules.common.schemas.response_schema import (
    PaginatedData,
    PaginationMeta,
    SuccessResponse,
    PaginationData,
    SuccessData,
    SuccessDataPaginated,
)

router = APIRouter(prefix="/demos")


@router.get("/", response_model=SuccessDataPaginated[DemoResponse])
@catch_error
async def list_demos(
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

    demos, pagination = await demo_service.get_demos(
        page=page,
        limit=limit,
        search=search,
        sort=sort,
        filters=filters,
    )

    return SuccessDataPaginated(
        message="Demos retrieved successfully",
        data=PaginatedData(
            meta=PaginationMeta(**pagination),
            docs=demos,
        ),
    )



@router.get("/{demo_id}", response_model=SuccessData[dict])
@catch_error
async def get_demo(request: Request, demo_id: str):

    demo = await demo_service.get_demo_by_id(demo_id)
    if not demo:
        raise HTTPException(status_code=404, detail="Demo not found")

    return SuccessData(message="Demo retrieved successfully", data=demo)


@router.post("/", response_model=SuccessData[dict], status_code=status.HTTP_201_CREATED)
@catch_error
async def create_demo(request: Request, demo_data: DemoCreate):

    demo = await demo_service.create_demo(demo_data)
    return SuccessData(message="Demo created successfully", data=demo)


@router.put("/{demo_id}", response_model=SuccessData[dict])
@catch_error
async def update_demo(request: Request, demo_id: str, demo_data: DemoUpdate):

    demo = await demo_service.update_demo(demo_id, demo_data)
    if not demo:
        raise HTTPException(status_code=404, detail="Demo not found")

    return SuccessData(message="Demo updated successfully", data=demo)


@router.patch("/{demo_id}/status", response_model=SuccessData[dict])
@catch_error
async def update_status(
    request: Request,
    demo_id: str,
    status_data: StatusEnum,
):
    demo = await demo_service.change_demo_status(demo_id, status_data)
    if not demo:
        raise HTTPException(status_code=404, detail="Demo not found")

    return SuccessData(message="Demo status updated successfully", data=demo)


@router.delete("/{demo_id}", response_model=SuccessResponse)
@catch_error
async def delete_demo(request: Request, demo_id: str):

    if not await demo_service.remove_demo(demo_id):
        raise HTTPException(status_code=404, detail="Demo not found")

    return SuccessResponse(message="Demo deleted successfully")
