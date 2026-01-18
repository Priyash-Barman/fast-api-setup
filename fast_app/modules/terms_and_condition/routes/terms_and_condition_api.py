from fastapi import APIRouter, status, Request
from typing import Optional

from fast_app.decorators.catch_error import catch_error
from fast_app.modules.terms_and_condition.services.terms_and_condition_service import (
    get_terms_and_condition,
)
from fast_app.modules.common.schemas.response_schema import (
    SuccessData,
)

router = APIRouter(
    prefix="/terms-and-condition",
)

@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=SuccessData[Optional[dict]],
)
@catch_error
async def get_terms_and_condition_api(request: Request):
    return await get_terms_and_condition()

