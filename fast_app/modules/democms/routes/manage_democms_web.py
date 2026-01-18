from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from jinja2 import ChoiceLoader, FileSystemLoader

from fast_app.modules.democms.schemas.democms_schema import (
    DemocmsUpdate,
)
from fast_app.modules.democms.services import democms_service
from fast_app.decorators.catch_error import catch_error

router = APIRouter(prefix="/admin/democms")

# Templates
templates = Jinja2Templates(directory="modules/democms/templates")
templates.env.loader = ChoiceLoader([
    FileSystemLoader("fast_app/modules/common/templates/layouts"),
    FileSystemLoader("fast_app/modules/democms/templates"),
])


# ----------------------------
# MANAGE PAGE (GET)
# ----------------------------
@router.get("")
@catch_error
async def manage_democms(request: Request):
    """
    Single page:
    - Shows existing CMS content (if any)
    - Otherwise empty editor
    """
    democms = await democms_service.get_single()

    return templates.TemplateResponse(
        "manage.html",
        {
            "request": request,
            "democms": democms,
        }
    )


# ----------------------------
# UPSERT (CREATE / UPDATE)
# ----------------------------
@router.post("")
@catch_error
async def save_democms(
    request: Request,
    form: DemocmsUpdate = Depends(DemocmsUpdate.as_form),
):
    """
    Upsert mode:
    - If record exists → update
    - Else → create
    """
    await democms_service.update_democms(form)

    return RedirectResponse(
        url="/admin/democms",
        status_code=status.HTTP_302_FOUND,
    )
