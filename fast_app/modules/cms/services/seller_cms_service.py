from typing import Any, Dict, List, Optional
from datetime import datetime

from fastapi import HTTPException, UploadFile, status
from beanie import PydanticObjectId

from fast_app.modules.cms.models.seller_cms_model import (
    SellerCms,
)
from fast_app.modules.cms.models.common_cms_model import Banner
from fast_app.modules.cms.schemas.seller_cms_schema import (
    SellerCmsCreate,
    SellerCmsUpdate,
)
from fast_app.utils.common_utils import exclude_unset
from fast_app.utils.file_utils import upload_files
from fast_app.utils.logger import logger


async def get_seller_cms() -> Dict[str, Any]:
    seller_cms = await SellerCms.find_one(
        SellerCms.is_deleted == False
    )

    return {
        "message": "Seller Cms retrieved successfully!",
        "data": seller_cms.model_dump(by_alias=True, mode="json")
        if seller_cms
        else None,
    }


async def create_seller_cms(
    data: SellerCmsCreate,
) -> Dict[str, Any]:

    # 🚫 Prevent multiple documents
    existing_policy = await SellerCms.find_one(
        SellerCms.is_deleted == False
    )
    if existing_policy:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Seller Cms already exists. Use update instead.",
        )

    try:
        seller_cms = SellerCms(**data.model_dump())
        await seller_cms.create()
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create Seller Cms, please try again",
        )

    return {
        "message": "Seller Cms created successfully",
        "data": seller_cms.model_dump(by_alias=True, mode="json"),
    }



async def update_seller_cms(
    data: SellerCmsUpdate,
) -> Dict[str, Any]:

    seller_cms = await SellerCms.find_one(
        SellerCms.is_deleted == False
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
        if not seller_cms:
            seller_cms = SellerCms(
                **update_data,
                is_deleted=False,
                created_at=datetime.utcnow(),
            )
            await seller_cms.create()
            message = "Seller Cms created successfully!"

        # 🔹 UPDATE (if exists)
        else:
            await seller_cms.set(update_data)
            message = "Seller Cms updated successfully!"

    except Exception as e:
        logger.error(str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to save Seller Cms, please try again",
        )

    return {
        "message": message,
        "data": seller_cms.model_dump(by_alias=True, mode="json"),
    }



async def remove_seller_cms() -> Dict[str, Any]:
    seller_cms = await SellerCms.find_one(
        SellerCms.is_deleted == False
    )

    if not seller_cms:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Seller Cms does not exist",
        )

    await seller_cms.set(
        {
            "is_deleted": True,
            "updated_at": datetime.utcnow(),
        }
    )

    return {
        "message": "Seller Cms removed successfully!",
    }
