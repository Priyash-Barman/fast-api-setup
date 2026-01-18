from fastapi import APIRouter, Depends, Request, Form, Query, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Optional, Dict

from jinja2 import ChoiceLoader, FileSystemLoader

from fast_app.modules.demoform.schemas.demoform_schema import DemoformCreateForm, DemoformUpdateForm
from fast_app.modules.demoform.services import demoform_service
from fast_app.decorators.catch_error import catch_error
from fast_app.defaults.common_enums import StatusEnum

router = APIRouter(prefix="/admin/demoforms")

# Template loaders
templates = Jinja2Templates(directory="modules/demoform/templates")
templates.env.loader = ChoiceLoader([
    FileSystemLoader("fast_app/modules/common/templates/layouts"),
    FileSystemLoader("fast_app/modules/demoform/templates"),
])


@router.get("/")
@catch_error
async def list_demoforms(
    request: Request,
    page: int = Query(1),
    search: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None),
):

    filters: Dict = {}
    if status_filter:
        filters["status"] = StatusEnum(status_filter)

    demoforms, pagination = await demoform_service.get_demoforms(
        page=page,
        search=search,
        filters=filters,
    )

    return templates.TemplateResponse("list.html", {
        "request": request,
        "demoforms": demoforms,
        "search": search,
        "status_filter": status_filter,
        "pagination": pagination,
    })


@router.get("/create")
@catch_error
async def create_form(request: Request):
    return templates.TemplateResponse("form.html", {"request": request, "demoform": None})


@router.post("/create")
@catch_error
async def create_demo(
    request: Request,
    form: DemoformCreateForm = Depends(DemoformCreateForm.as_form)
):

    await demoform_service.create_demoform(form)

    return RedirectResponse(url="/admin/demoforms", status_code=status.HTTP_302_FOUND)


@router.get("/{demoform_id}/edit")
@catch_error
async def edit_form(request: Request, demoform_id: str):

    demoform = await demoform_service.get_demoform_by_id(demoform_id)
    if not demoform:
        return RedirectResponse(url="/admin/demoforms", status_code=302)

    return templates.TemplateResponse("form.html", {
        "request": request,
        "demoform": demoform,
    })


@router.post("/{demoform_id}/edit")
@catch_error
async def update_demoform(
    request: Request,
    demoform_id: str,
    form: DemoformUpdateForm=Depends(DemoformUpdateForm.as_form)
):
    await demoform_service.update_demoform(
        demoform_id,
        form,
    )

    return RedirectResponse(url="/admin/demoforms", status_code=302)


@router.get("/{demoform_id}/delete")
@catch_error
async def delete_demoform(request: Request, demoform_id: str):

    await demoform_service.remove_demoform(demoform_id)
    return RedirectResponse(url="/admin/demoforms", status_code=302)


# ----------------------------
# TOGGLE ACTIVE/INACTIVE
# ----------------------------
@router.get("/{demoform_id}/toggle", name="admin_demoforms:toggle_status")
@catch_error
async def toggle_demoform_status(request: Request, demoform_id: str):
    demoform = await demoform_service.get_demoform_by_id(demoform_id)

    if demoform:
        print(demoform)
        await demoform_service.change_demoform_status(demoform_id, StatusEnum.ACTIVE if demoform.get('status')==StatusEnum.INACTIVE else StatusEnum.INACTIVE)

    return RedirectResponse(url="/admin/demoforms", status_code=status.HTTP_302_FOUND)
