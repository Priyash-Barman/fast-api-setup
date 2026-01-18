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
from fast_app.modules.cms.schemas.seller_cms_schema import (
    SellerCmsCreate,
    SellerCmsUpdate,
)
from fast_app.modules.cms.services.seller_cms_service import (
    get_seller_cms,
    create_seller_cms,
    update_seller_cms,
    remove_seller_cms,
)
from fast_app.modules.common.schemas.response_schema import (
    SuccessData,
    SuccessResponse,
)


router = APIRouter(prefix="/admin/seller-cms")


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=SuccessData[dict],
)
@catch_error
@login_required(UserRole.ADMIN)
async def create_seller_cms_api(
    request: Request,
    data: SellerCmsCreate,
):
    return await create_seller_cms(data)

@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=SuccessData[Optional[dict]],
)
@catch_error
@login_required(UserRole.ADMIN)
async def get_seller_cms_api(
    request: Request,
):
    return await get_seller_cms()


@router.patch(
    "",
    status_code=status.HTTP_200_OK,
    response_model=SuccessData[dict],
)
@catch_error
@login_required(UserRole.ADMIN)
async def update_seller_cms_api(
    request: Request,
    data: SellerCmsUpdate,
):
    return await update_seller_cms(data)


@router.delete(
    "",
    status_code=status.HTTP_200_OK,
    response_model=SuccessResponse,
)
@catch_error
@login_required(UserRole.ADMIN)
async def delete_seller_cms_api(
    request: Request,
):
    return await remove_seller_cms()


