from fastapi import APIRouter, status, Request
from typing import Optional

from fast_app.decorators.catch_error import catch_error
from fast_app.modules.cms.services.buyer_cms_service import (
    get_buyer_cms,
)
from fast_app.modules.common.schemas.response_schema import (
    SuccessData,
)

router = APIRouter(
    prefix="/buyer-cms",
)

@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=SuccessData[Optional[dict]],
)
@catch_error
async def get_buyer_cms_api(request: Request):
    return await get_buyer_cms()

