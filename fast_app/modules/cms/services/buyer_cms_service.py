from typing import Any, Dict, List, Optional
from datetime import datetime

from fastapi import HTTPException, UploadFile, status
from beanie import PydanticObjectId

from fast_app.modules.cms.models.buyer_cms_model import (
    BuyerCms,
)
from fast_app.modules.cms.models.common_cms_model import Banner
from fast_app.modules.cms.schemas.buyer_cms_schema import (
    BuyerCmsCreate,
    BuyerCmsUpdate,
)
from fast_app.utils.common_utils import exclude_unset
from fast_app.utils.file_utils import upload_files
from fast_app.utils.logger import logger


async def get_buyer_cms() -> Dict[str, Any]:
    buyer_cms = await BuyerCms.find_one(
        BuyerCms.is_deleted == False
    )

    return {
        "message": "Buyer Cms retrieved successfully!",
        "data": buyer_cms.model_dump(by_alias=True, mode="json")
        if buyer_cms
        else None,
    }


async def create_buyer_cms(
    data: BuyerCmsCreate,
) -> Dict[str, Any]:

    # 🚫 Prevent multiple documents
    existing_policy = await BuyerCms.find_one(
        BuyerCms.is_deleted == False
    )
    if existing_policy:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Buyer Cms already exists. Use update instead.",
        )

    try:
        buyer_cms = BuyerCms(**data.model_dump())
        await buyer_cms.create()
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create Buyer Cms, please try again",
        )

    return {
        "message": "Buyer Cms created successfully",
        "data": buyer_cms.model_dump(by_alias=True, mode="json"),
    }



async def update_buyer_cms(
    data: BuyerCmsUpdate,
) -> Dict[str, Any]:

    buyer_cms = await BuyerCms.find_one(
        BuyerCms.is_deleted == False
    )

    update_data = data.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No data provided to update",
        )

    update_data["updated_at"] = datetime.utcnow()

    try:
        # 🔹 CREATE (if not exists)
        if not buyer_cms:
            buyer_cms = BuyerCms(
                **update_data,
                is_deleted=False,
                created_at=datetime.utcnow(),
            )
            await buyer_cms.create()
            message = "Buyer Cms created successfully!"

        # 🔹 UPDATE (if exists)
        else:
            await buyer_cms.set(update_data)
            message = "Buyer Cms updated successfully!"

    except Exception as e:
        logger.error(str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to save Buyer Cms, please try again",
        )

    return {
        "message": message,
        "data": buyer_cms.model_dump(by_alias=True, mode="json"),
    }



async def remove_buyer_cms() -> Dict[str, Any]:
    buyer_cms = await BuyerCms.find_one(
        BuyerCms.is_deleted == False
    )

    if not buyer_cms:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Buyer Cms does not exist",
        )

    await buyer_cms.set(
        {
            "is_deleted": True,
            "updated_at": datetime.utcnow(),
        }
    )

    return {
        "message": "Buyer Cms removed successfully!",
    }
