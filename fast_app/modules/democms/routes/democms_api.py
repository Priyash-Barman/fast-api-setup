from fastapi import APIRouter, status, Request
from typing import Optional

from fast_app.decorators.catch_error import catch_error
from fast_app.modules.democms.services.democms_service import (
    get_democms,
)
from fast_app.modules.common.schemas.response_schema import (
    SuccessData,
)

router = APIRouter(
    prefix="/democms",
)

@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=SuccessData[Optional[dict]],
)
@catch_error
async def get_democms_api(request: Request):
    return await get_democms()

