from fastapi import (
    APIRouter,
    Depends,
    status,
    Request,
)
from typing import Optional

from fast_app.decorators.authenticator import login_required
from fast_app.decorators.catch_error import catch_error
from fast_app.defaults.common_enums import UserRole
from fast_app.modules.cms.schemas.buyer_cms_schema import (
    BuyerCmsCreate,
    BuyerCmsUpdate,
)
from fast_app.modules.cms.services.buyer_cms_service import (
    get_buyer_cms,
    create_buyer_cms,
    update_buyer_cms,
    remove_buyer_cms,
)
from fast_app.modules.common.schemas.response_schema import (
    SuccessData,
    SuccessResponse,
)


router = APIRouter(prefix="/admin/buyer-cms")


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=SuccessData[dict],
)
@catch_error
@login_required(UserRole.ADMIN)
async def create_buyer_cms_api(
    request: Request,
    data: BuyerCmsCreate,
):
    return await create_buyer_cms(data)

@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=SuccessData[Optional[dict]],
)
@catch_error
@login_required(UserRole.ADMIN)
async def get_buyer_cms_api(
    request: Request,
):
    return await get_buyer_cms()


@router.patch(
    "",
    status_code=status.HTTP_200_OK,
    response_model=SuccessData[dict],
)
@catch_error
@login_required(UserRole.ADMIN)
async def update_buyer_cms_api(
    request: Request,
    data: BuyerCmsUpdate,
):
    return await update_buyer_cms(data)


@router.delete(
    "",
    status_code=status.HTTP_200_OK,
    response_model=SuccessResponse,
)
@catch_error
@login_required(UserRole.ADMIN)
async def delete_buyer_cms_api(
    request: Request,
):
    return await remove_buyer_cms()


