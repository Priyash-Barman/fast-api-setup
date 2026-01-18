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
from fast_app.modules.privacy_policy.schemas.privacy_policy_schema import (
    PrivacyPolicyCreate,
    PrivacyPolicyUpdate,
)
from fast_app.modules.privacy_policy.services.privacy_policy_service import (
    get_privacy_policy,
    create_privacy_policy,
    update_privacy_policy,
    remove_privacy_policy,
)
from fast_app.modules.common.schemas.response_schema import (
    SuccessData,
    SuccessResponse,
)


router = APIRouter(prefix="/admin/privacy-policy")


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=SuccessData[dict],
)
@catch_error
@login_required(UserRole.ADMIN)
async def create_privacy_policy_api(
    request: Request,
    data: PrivacyPolicyCreate = Depends(PrivacyPolicyCreate.as_form),
):
    return await create_privacy_policy(data)

@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=SuccessData[Optional[dict]],
)
@catch_error
@login_required(UserRole.ADMIN)
async def get_privacy_policy_api(
    request: Request,
):
    return await get_privacy_policy()


@router.patch(
    "",
    status_code=status.HTTP_200_OK,
    response_model=SuccessData[dict],
)
@catch_error
@login_required(UserRole.ADMIN)
async def update_privacy_policy_api(
    request: Request,
    data: PrivacyPolicyUpdate = Depends(PrivacyPolicyUpdate.as_form),
):
    return await update_privacy_policy(data)


@router.delete(
    "",
    status_code=status.HTTP_200_OK,
    response_model=SuccessResponse,
)
@catch_error
@login_required(UserRole.ADMIN)
async def delete_privacy_policy_api(
    request: Request,
):
    return await remove_privacy_policy()


