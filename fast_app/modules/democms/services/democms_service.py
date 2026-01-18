from typing import Any, Dict, List, Optional
from datetime import datetime

from fastapi import HTTPException, UploadFile, status
from beanie import PydanticObjectId

from fast_app.modules.democms.models.democms_model import (
    Democms,
)
from fast_app.modules.democms.schemas.democms_schema import (
    DemocmsCreate,
    DemocmsUpdate,
)
from fast_app.utils.common_utils import exclude_unset
from fast_app.utils.file_utils import upload_files
from fast_app.utils.logger import logger


async def get_democms() -> Dict[str, Any]:
    democms = await Democms.find_one(
        Democms.is_deleted == False
    )

    return {
        "message": "Democms retrieved successfully!",
        "data": democms.model_dump(by_alias=True, mode="json")
        if democms
        else None,
    }


async def create_democms(
    data: DemocmsCreate,
) -> Dict[str, Any]:

    # 🚫 Prevent multiple documents
    existing_policy = await Democms.find_one(
        Democms.is_deleted == False
    )
    if existing_policy:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Democms already exists. Use update instead.",
        )

    image_path = ""
    print(data)

    # 🖼 Upload image
    if data.image:
        uploaded = await upload_files([data.image], "democms")
        image_path = uploaded[0].get("path", "")

    try:
        democms = Democms(
            content=data.content,
            image=image_path,
        )
        await democms.create()
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create Democms, please try again",
        )

    return {
        "message": "Democms created successfully",
        "data": democms.model_dump(by_alias=True, mode="json"),
    }



async def update_democms(
    data: DemocmsUpdate,
) -> Dict[str, Any]:

    democms = await Democms.find_one(
        Democms.is_deleted == False
    )

    update_data = data.model_dump(exclude_unset=True)

    # 🖼 Upload image
    if data.image:
        uploaded = await upload_files([data.image], "democms")
        update_data["image"] = uploaded[0].get("path", "")

    if data.remove_image:
        update_data["image"] = ""
    elif data.remove_image == False and data.image and democms:
        update_data["image"] = democms.image


    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No data provided to update",
        )

    update_data["updated_at"] = datetime.utcnow()

    try:
        # 🔹 CREATE (if not exists)
        if not democms:
            democms = Democms(
                **update_data,
                is_deleted=False,
                created_at=datetime.utcnow(),
            )
            await democms.create()
            message = "Democms created successfully!"

        # 🔹 UPDATE (if exists)
        else:
            await democms.set(update_data)
            message = "Democms updated successfully!"

    except Exception as e:
        logger.error(str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to save Democms, please try again",
        )

    return {
        "message": message,
        "data": democms.model_dump(by_alias=True, mode="json"),
    }



async def remove_democms() -> Dict[str, Any]:
    democms = await Democms.find_one(
        Democms.is_deleted == False
    )

    if not democms:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Democms does not exist",
        )

    await democms.set(
        {
            "is_deleted": True,
            "updated_at": datetime.utcnow(),
        }
    )

    return {
        "message": "Democms removed successfully!",
    }

async def get_single():
        return await Democms.find_one({"is_deleted": False})