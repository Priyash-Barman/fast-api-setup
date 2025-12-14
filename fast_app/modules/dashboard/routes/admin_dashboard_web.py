from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

# from decorators.authenticator import login_required
from fast_app.decorators.catch_error import catch_error
from fast_app.utils.logger import logger
from jinja2 import ChoiceLoader, FileSystemLoader

router = APIRouter(prefix="/admin")
# Setup templates loader for this module with access to common layouts
templates = Jinja2Templates(directory="modules/dashboard/templates")
templates.env.loader = ChoiceLoader([
    FileSystemLoader("fast_app/modules/common/templates/layouts"),  # common layouts
    FileSystemLoader("fast_app/modules/dashboard/templates"),             # module templates
])


@router.get("/", name="admin_dashboard")
@catch_error
# @login_required("admin")
async def dashboard(request: Request):
    logger.info(f"Welcome to admin dashboard")
    return templates.TemplateResponse("admin_dashboard.html",{"request":request})

