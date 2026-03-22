from fastapi import APIRouter, Request, Form, Query, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Optional, Dict

from jinja2 import ChoiceLoader, FileSystemLoader

from fast_app.modules.mobile.schemas.mobile_schema import MobileCreate, MobileUpdate
from fast_app.modules.mobile.services import mobile_service
from fast_app.decorators.catch_error import catch_error
from fast_app.defaults.common_enums import StatusEnum

router = APIRouter(prefix="/admin/mobiles")

# Template loaders
templates = Jinja2Templates(directory="modules/mobile/templates")
templates.env.loader = ChoiceLoader([
    FileSystemLoader("fast_app/modules/common/templates/layouts"),
    FileSystemLoader("fast_app/modules/mobile/templates"),
])


@router.get("/")
@catch_error
async def list_mobiles(
    request: Request,
    page: int = Query(1),
    search: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None),
):

    filters: Dict = {}
    if status_filter:
        filters["status"] = StatusEnum(status_filter)

    mobiles, pagination = await mobile_service.get_mobiles(
        page=page,
        search=search,
        filters=filters,
    )

    return templates.TemplateResponse("list.html", {
        "request": request,
        "mobiles": mobiles,
        "search": search,
        "status_filter": status_filter,
        "pagination": pagination,
    })


@router.get("/create")
@catch_error
async def create_form(request: Request):
    return templates.TemplateResponse("form.html", {"request": request, "mobile": None})


@router.post("/create")
@catch_error
async def create_mobile(
    request: Request,
    name: str = Form(...),
    description: str = Form(...),
):

    await mobile_service.create_mobile(
        MobileCreate
        (name=name, description=description)
    )

    return RedirectResponse(url="/admin/mobiles", status_code=status.HTTP_302_FOUND)


@router.get("/{mobile_id}/edit")
@catch_error
async def edit_form(request: Request, mobile_id: str):

    mobile = await mobile_service.get_mobile_by_id(mobile_id)
    if not mobile:
        return RedirectResponse(url="/admin/mobiles", status_code=302)

    return templates.TemplateResponse("form.html", {
        "request": request,
        "mobile": mobile,
    })


@router.post("/{mobile_id}/edit")
@catch_error
async def update_mobile(
    request: Request,
    mobile_id: str,
    name: str = Form(...),
    description: str = Form(...),
    status: StatusEnum = Form(...),
):

    await mobile_service.update_mobile(
        mobile_id,
        MobileUpdate(name=name, description=description, status=status),
    )

    return RedirectResponse(url="/admin/mobiles", status_code=302)


@router.get("/{mobile_id}/delete")
@catch_error
async def delete_mobile(request: Request, mobile_id: str):

    await mobile_service.remove_mobile(mobile_id)
    return RedirectResponse(url="/admin/mobiles", status_code=302)


# ----------------------------
# TOGGLE ACTIVE/INACTIVE
# ----------------------------
@router.get("/{mobile_id}/toggle", name="admin_mobiles:toggle_status")
@catch_error
async def toggle_mobile_status(request: Request, mobile_id: str):
    mobile = await mobile_service.get_mobile_by_id(mobile_id)

    if mobile:
        print(mobile)
        await mobile_service.change_mobile_status(mobile_id, StatusEnum.ACTIVE if mobile.get('status')==StatusEnum.INACTIVE else StatusEnum.INACTIVE)

    return RedirectResponse(url="/admin/mobiles", status_code=status.HTTP_302_FOUND)
