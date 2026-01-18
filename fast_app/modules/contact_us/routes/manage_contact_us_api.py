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
from fast_app.modules.contact_us.schemas.contact_us_schema import (
    ContactUsCreate,
    ContactUsUpdate,
)
from fast_app.modules.contact_us.services.contact_us_service import (
    get_contact_us,
    create_contact_us,
    update_contact_us,
    remove_contact_us,
)
from fast_app.modules.common.schemas.response_schema import (
    SuccessData,
    SuccessResponse,
)


router = APIRouter(prefix="/admin/contact-us")


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=SuccessData[dict],
)
@catch_error
@login_required(UserRole.ADMIN)
async def create_contact_us_api(
    request: Request,
    data: ContactUsCreate = Depends(ContactUsCreate.as_form),
):
    return await create_contact_us(data)

@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=SuccessData[Optional[dict]],
)
@catch_error
@login_required(UserRole.ADMIN)
async def get_contact_us_api(
    request: Request,
):
    return await get_contact_us()


@router.patch(
    "",
    status_code=status.HTTP_200_OK,
    response_model=SuccessData[dict],
)
@catch_error
@login_required(UserRole.ADMIN)
async def update_contact_us_api(
    request: Request,
    data: ContactUsUpdate = Depends(ContactUsUpdate.as_form),
):
    return await update_contact_us(data)


@router.delete(
    "",
    status_code=status.HTTP_200_OK,
    response_model=SuccessResponse,
)
@catch_error
@login_required(UserRole.ADMIN)
async def delete_contact_us_api(
    request: Request,
):
    return await remove_contact_us()


