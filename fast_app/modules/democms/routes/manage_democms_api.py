from fastapi import (
    APIRouter,
    Depends,
    status,
    Request,
)
from typing import Optional

from fast_app.decorators.catch_error import catch_error
from fast_app.defaults.common_enums import UserRole
from fast_app.modules.democms.schemas.democms_schema import (
    DemocmsCreate,
    DemocmsUpdate,
)
from fast_app.modules.democms.services.democms_service import (
    get_democms,
    create_democms,
    update_democms,
    remove_democms,
)
from fast_app.modules.common.schemas.response_schema import (
    SuccessData,
    SuccessResponse,
)


router = APIRouter(prefix="/admin/democms")


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=SuccessData[dict],
)
@catch_error
async def create_democms_api(
    request: Request,
    data: DemocmsCreate = Depends(DemocmsCreate.as_form),
):
    return await create_democms(data)

@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=SuccessData[Optional[dict]],
)
@catch_error
async def get_democms_api(
    request: Request,
):
    return await get_democms()


@router.patch(
    "",
    status_code=status.HTTP_200_OK,
    response_model=SuccessData[dict],
)
@catch_error
async def update_democms_api(
    request: Request,
    data: DemocmsUpdate = Depends(DemocmsUpdate.as_form),
):
    return await update_democms(data)


@router.delete(
    "",
    status_code=status.HTTP_200_OK,
    response_model=SuccessResponse,
)
@catch_error
async def delete_democms_api(
    request: Request,
):
    return await remove_democms()

