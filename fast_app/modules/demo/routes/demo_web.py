from fastapi import APIRouter, Request, Form, Query, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Optional, Dict

from jinja2 import ChoiceLoader, FileSystemLoader

from fast_app.modules.demo.schemas.demo_schema import DemoCreate, DemoUpdate
from fast_app.modules.demo.services import demo_service
from fast_app.decorators.catch_error import catch_error
from fast_app.defaults.common_enums import StatusEnum

router = APIRouter(prefix="/admin/demos")

# Template loaders
templates = Jinja2Templates(directory="modules/demo/templates")
templates.env.loader = ChoiceLoader([
    FileSystemLoader("fast_app/modules/common/templates/layouts"),
    FileSystemLoader("fast_app/modules/demo/templates"),
])


@router.get("/")
@catch_error
async def list_demos(
    request: Request,
    page: int = Query(1),
    search: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None),
):

    filters: Dict = {}
    if status_filter:
        filters["status"] = StatusEnum(status_filter)

    demos, pagination = await demo_service.get_demos(
        page=page,
        search=search,
        filters=filters,
    )

    return templates.TemplateResponse("list.html", {
        "request": request,
        "demos": demos,
        "search": search,
        "status_filter": status_filter,
        "pagination": pagination,
    })


@router.get("/create")
@catch_error
async def create_form(request: Request):
    return templates.TemplateResponse("form.html", {"request": request, "demo": None})


@router.post("/create")
@catch_error
async def create_demo(
    request: Request,
    name: str = Form(...),
    description: str = Form(...),
):

    await demo_service.create_demo(
        DemoCreate
        (name=name, description=description)
    )

    return RedirectResponse("/admin/demos", status_code=status.HTTP_302_FOUND)


@router.get("/{demo_id}/edit")
@catch_error
async def edit_form(request: Request, demo_id: str):

    demo = await demo_service.get_demo_by_id(demo_id)
    if not demo:
        return RedirectResponse("/admin/demos", status_code=302)

    return templates.TemplateResponse("form.html", {
        "request": request,
        "demo": demo,
    })


@router.post("/{demo_id}/edit")
@catch_error
async def update_demo(
    request: Request,
    demo_id: str,
    name: str = Form(...),
    description: str = Form(...),
    status: StatusEnum = Form(...),
):

    await demo_service.update_demo(
        demo_id,
        DemoUpdate(name=name, description=description, status=status),
    )

    return RedirectResponse("/admin/demos", status_code=302)


@router.get("/{demo_id}/delete")
@catch_error
async def delete_demo(request: Request, demo_id: str):

    await demo_service.remove_demo(demo_id)
    return RedirectResponse("/admin/demos", status_code=302)


# ----------------------------
# TOGGLE ACTIVE/INACTIVE
# ----------------------------
@router.get("/{demo_id}/toggle", name="admin_demos:toggle_status")
@catch_error
async def toggle_user_status(request: Request, demo_id: str):
    demo = await demo_service.get_demo_by_id(demo_id)

    if demo:
        print(demo)
        await demo_service.change_demo_status(demo_id, StatusEnum.ACTIVE if demo.get('status')==StatusEnum.INACTIVE else StatusEnum.INACTIVE)

    return RedirectResponse(url="/admin/demos", status_code=status.HTTP_302_FOUND)
