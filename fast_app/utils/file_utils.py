import os
import uuid
import asyncio
from datetime import datetime
from typing import Any, List, Dict
import aiobotocore.session
from fastapi import HTTPException, UploadFile, status
from fast_app.utils.logger import logger

from config import (
    AWS_S3_BUCKET_ACCESS_KEY,
    AWS_S3_BUCKET_HOST,
    AWS_S3_BUCKET_NAME,
    AWS_S3_BUCKET_REGION,
    AWS_S3_BUCKET_SECRET_KEY,
    BUCKET,
)


ALLOWED_TYPES = {
    "image/jpeg": b"\xff\xd8\xff",
    "image/png": b"\x89PNG\r\n\x1a\n",
    "image/webp": b"RIFF",
}

MAX_SIZE = 5 * 1024 * 1024  # 5 MB


# -----------------------------------------------------
# MAIN UPLOAD HANDLER
# -----------------------------------------------------
async def upload_files(
    files: List[UploadFile],
    dir: str = "default",
) -> List[Dict[str, Any]]:
    try:
        if BUCKET == "local":
            return await local_upload(files, dir)
        elif BUCKET == "s3":
            return await s3_upload(files, dir)
        else:
            logger.warning("Invalid bucket selected")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid bucket selected",
            )
    except Exception as e:
        logger.error(f"File upload failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Something went wrong while uploading file",
        )


# -----------------------------------------------------
# LOCAL UPLOAD
# -----------------------------------------------------
async def local_upload(
    files: List[UploadFile],
    dir: str = "default",
) -> List[Dict[str, Any]]:
    STATIC_DIR = os.path.join("fast_app", "static", "uploads")

    # Generate file keys
    file_keys = [
        _generate_file_key(f.filename or "untitled", dir)
        for f in files
    ]

    async def upload_file(file: UploadFile, file_key: str) -> Dict[str, Any]:
        if not await validate_file(file):
            return {}
        file_path = os.path.join(STATIC_DIR, file_key)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)

        return {
            "original_name": file.filename,
            "file_key": file_key,
            "url": f"/static/uploads/{file_key}",
            "size": len(contents),
            "path": f"/static/uploads/{file_key}",
        }

    tasks = [
        upload_file(file, key)
        for file, key in zip(files, file_keys)
    ]

    return await asyncio.gather(*tasks)


# -----------------------------------------------------
# S3 UPLOAD
# -----------------------------------------------------
async def s3_upload(
    files: List[UploadFile],
    dir: str = "uploads",
) -> List[Dict[str, Any]]:
    BUCKET_NAME = AWS_S3_BUCKET_NAME
    REGION = AWS_S3_BUCKET_REGION
    ACCESS_KEY = AWS_S3_BUCKET_ACCESS_KEY
    SECRET_KEY = AWS_S3_BUCKET_SECRET_KEY
    BUCKET_HOST = AWS_S3_BUCKET_HOST

    file_keys = [
        _generate_file_key(f.filename or "untitled", dir)
        for f in files
    ]

    session = aiobotocore.session.get_session()

    async def upload_file(file: UploadFile, file_key: str) -> Dict[str, Any]:
        if not await validate_file(file):
            return {}
        async with session.create_client(
            "s3",
            region_name=REGION,
            aws_access_key_id=ACCESS_KEY,
            aws_secret_access_key=SECRET_KEY,
            endpoint_url=f"https://{BUCKET_HOST}",
        ) as client:

            contents = await file.read()
            await client.put_object(
                Bucket=BUCKET_NAME,
                Key=file_key,
                Body=contents,
                ContentType=file.content_type or "application/octet-stream",
                ACL="public-read",
            )

            return {
                "original_name": file.filename,
                "s3_key": file_key,
                "url": f"https://{BUCKET_HOST}/{BUCKET_NAME}/{file_key}",
                "size": len(contents),
                "path": f"/{BUCKET_NAME}/{file_key}",
            }

    tasks = [
        upload_file(file, key)
        for file, key in zip(files, file_keys)
    ]

    return await asyncio.gather(*tasks)


# -----------------------------------------------------
# FILE KEY GENERATOR
# -----------------------------------------------------
def _generate_file_key(filename: str, dir: str) -> str:
    """Generate unique file key with sub-directory"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    _, ext = os.path.splitext(filename)

    dir = dir.strip("/")

    return f"{dir}/{timestamp}_{unique_id}{ext}"


async def validate_file(file: UploadFile | None) -> UploadFile | None:
    """
    Validates an uploaded image file.

    - Returns None if file is None or size is 0
    - Validates max size
    - Validates content type
    - Validates magic bytes
    """

    if not file:
        return None

    contents = await file.read()
    size = len(contents)

    # Treat empty file as no file
    if size == 0:
        await file.seek(0)
        return None

    print(f"Image size: {size} bytes")

    if size > MAX_SIZE:
        raise HTTPException(status_code=400, detail="Image too large")

    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Invalid image type")

    magic = ALLOWED_TYPES[file.content_type]
    if not contents.startswith(magic):
        raise HTTPException(status_code=400, detail="Invalid image file")

    # IMPORTANT: reset pointer for further use
    await file.seek(0)

    return file
