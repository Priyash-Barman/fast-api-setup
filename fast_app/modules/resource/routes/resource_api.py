from typing import Dict
from fastapi import HTTPException, Query, status, Request

from fast_app.core.router_context import RouterContext
from fast_app.defaults.permission_enums import Action, Resource
from fast_app.modules.resource.services import resource_service
from fast_app.decorators.catch_error import catch_error


from fast_app.modules.common.schemas.response_schema import SuccessData

router = RouterContext(prefix="/resources", name=Resource.RESOURCE)


@router.get("", response_model=SuccessData[Dict[str, Resource]])
@catch_error
async def get_resources(request: Request):

    return SuccessData(message="Resource retrieved successfully", data=resource_service.get_resources())


@router.get("/actions", response_model=SuccessData[Dict[str, Action]])
@catch_error
async def get_all_actions(request: Request):

    return SuccessData(message="Actions retrieved successfully", data=resource_service.get_actions())