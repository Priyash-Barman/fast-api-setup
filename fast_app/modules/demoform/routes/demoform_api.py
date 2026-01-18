from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from fast_app.decorators.catch_error import catch_error
from fast_app.defaults.common_enums import StatusEnum
from fast_app.modules.common.schemas.response_schema import (
    PaginatedData, PaginationData, PaginationMeta, SuccessData,
    SuccessDataPaginated, SuccessResponse)
from fast_app.modules.demoform.schemas.demoform_schema import (
    DemoformCreateForm, DemoformResponse, DemoformUpdateForm)
from fast_app.modules.demoform.services import demoform_service

router = APIRouter(prefix="/demoforms")


@router.get("/", response_model=SuccessDataPaginated[DemoformResponse])
@catch_error
async def list_demoforms(
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

    demoforms, pagination = await demoform_service.get_demoforms(
        page=page,
        limit=limit,
        search=search,
        sort=sort,
        filters=filters,
    )

    return SuccessDataPaginated(
        message="Demoforms retrieved successfully",
        data=PaginatedData(
            meta=PaginationMeta(**pagination),
            docs=demoforms,
        ),
    )



@router.get("/{demoform_id}", response_model=SuccessData[dict])
@catch_error
async def get_demoform(request: Request, demoform_id: str):

    demoform = await demoform_service.get_demoform_by_id(demoform_id)
    if not demoform:
        raise HTTPException(status_code=404, detail="Demoform not found")

    return SuccessData(message="Demoform retrieved successfully", data=demoform)


@router.post("/", response_model=SuccessData[dict], status_code=status.HTTP_201_CREATED)
@catch_error
async def create_demoform(request: Request, form: DemoformCreateForm = Depends(DemoformCreateForm.as_form)):

    demoform = await demoform_service.create_demoform(form)
    return SuccessData(message="Demoform created successfully", data=demoform)


@router.put("/{demoform_id}", response_model=SuccessData[dict])
@catch_error
async def update_demoform(request: Request, demoform_id: str, form: DemoformUpdateForm = Depends(DemoformUpdateForm.as_form)):

    demoform = await demoform_service.update_demoform(demoform_id, form)
    if not demoform:
        raise HTTPException(status_code=404, detail="Demoform not found")

    return SuccessData(message="Demoform updated successfully", data=demoform)


@router.patch("/{demoform_id}/status", response_model=SuccessData[dict])
@catch_error
async def update_status(
    request: Request,
    demoform_id: str,
    status_data: StatusEnum,
):
    demoform = await demoform_service.change_demoform_status(demoform_id, status_data)
    if not demoform:
        raise HTTPException(status_code=404, detail="Demoform not found")

    return SuccessData(message="Demoform status updated successfully", data=demoform)


@router.delete("/{demoform_id}", response_model=SuccessResponse)
@catch_error
async def delete_demoform(request: Request, demoform_id: str):

    if not await demoform_service.remove_demoform(demoform_id):
        raise HTTPException(status_code=404, detail="Demoform not found")

    return SuccessResponse(message="Demoform deleted successfully")
