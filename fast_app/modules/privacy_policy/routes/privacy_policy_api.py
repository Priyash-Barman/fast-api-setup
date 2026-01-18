from fastapi import APIRouter, status, Request
from typing import Optional

from fast_app.decorators.catch_error import catch_error
from fast_app.modules.privacy_policy.services.privacy_policy_service import (
    get_privacy_policy,
)
from fast_app.modules.common.schemas.response_schema import (
    SuccessData,
)

router = APIRouter(
    prefix="/privacy-policy",
)

@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=SuccessData[Optional[dict]],
)
@catch_error
async def get_privacy_policy_api(request: Request):
    return await get_privacy_policy()

