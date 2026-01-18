from fastapi import APIRouter, status, Request
from typing import Optional

from fast_app.decorators.catch_error import catch_error
from fast_app.modules.contact_us.services.contact_us_service import (
    get_contact_us,
)
from fast_app.modules.common.schemas.response_schema import (
    SuccessData,
)

router = APIRouter(
    prefix="/contact-us",
)

@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=SuccessData[Optional[dict]],
)
@catch_error
async def get_contact_us_api(request: Request):
    return await get_contact_us()

