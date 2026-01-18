from fastapi import APIRouter, Depends, status, Request
from typing import Optional

from fast_app.decorators.authenticator import login_required
from fast_app.decorators.catch_error import catch_error
from fast_app.modules.file.schemas import MultipleFileUploadSchema, SingleFileUploadSchema
from fast_app.modules.common.schemas.response_schema import (
    SuccessData,
)
from fast_app.utils.file_utils import upload_files

router = APIRouter(
    prefix="",
)


@router.post(
    "upload-file/multiple",
    status_code=status.HTTP_200_OK,
    response_model=SuccessData[Optional[dict]],
)
@catch_error
@login_required()
async def multiple_upload_file(request: Request, data: MultipleFileUploadSchema = Depends(MultipleFileUploadSchema.as_form)):
    file_path = []

    # 🖼 Upload file
    if len(data.files):
        uploaded = await upload_files(data.files, data.path or "common")
        file_path=[up.get("path", "") for up in uploaded]
    return SuccessData(
        message="File uploaded successfully",
        data={"file_path": file_path},
    )


@router.post(
    "upload-file/single",
    status_code=status.HTTP_200_OK,
    response_model=SuccessData[Optional[dict]],
)
@catch_error
@login_required()
async def single_upload_file(request: Request, data: SingleFileUploadSchema = Depends(SingleFileUploadSchema.as_form)):
    file_path = ""

    # 🖼 Upload file
    if data.file:
        uploaded = await upload_files([data.file], data.path or "common")
        file_path = uploaded[0].get("path", "")
    return SuccessData(
        message="File uploaded successfully",
        data={"file_path": file_path},
    )
