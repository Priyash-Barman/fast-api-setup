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
from fast_app.modules.terms_and_condition.schemas.terms_and_condition_schema import (
    TermsAndConditionCreate,
    TermsAndConditionUpdate,
)
from fast_app.modules.terms_and_condition.services.terms_and_condition_service import (
    get_terms_and_condition,
    create_terms_and_condition,
    update_terms_and_condition,
    remove_terms_and_condition,
)
from fast_app.modules.common.schemas.response_schema import (
    SuccessData,
    SuccessResponse,
)


router = APIRouter(prefix="/admin/terms-and-condition")


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=SuccessData[dict],
)
@catch_error
@login_required(UserRole.ADMIN)
async def create_terms_and_condition_api(
    request: Request,
    data: TermsAndConditionCreate = Depends(TermsAndConditionCreate.as_form),
):
    return await create_terms_and_condition(data)

@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=SuccessData[Optional[dict]],
)
@catch_error
@login_required(UserRole.ADMIN)
async def get_terms_and_condition_api(
    request: Request,
):
    return await get_terms_and_condition()


@router.patch(
    "",
    status_code=status.HTTP_200_OK,
    response_model=SuccessData[dict],
)
@catch_error
@login_required(UserRole.ADMIN)
async def update_terms_and_condition_api(
    request: Request,
    data: TermsAndConditionUpdate = Depends(TermsAndConditionUpdate.as_form),
):
    return await update_terms_and_condition(data)


@router.delete(
    "",
    status_code=status.HTTP_200_OK,
    response_model=SuccessResponse,
)
@catch_error
@login_required(UserRole.ADMIN)
async def delete_terms_and_condition_api(
    request: Request,
):
    return await remove_terms_and_condition()


