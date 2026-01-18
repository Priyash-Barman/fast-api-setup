from typing import Any, Dict, List, Optional
from datetime import datetime

from fastapi import HTTPException, UploadFile, status
from beanie import PydanticObjectId

from fast_app.modules.contact_us.models.contact_us_model import (
    ContactUs,
)
from fast_app.modules.contact_us.schemas.contact_us_schema import (
    ContactUsCreate,
    ContactUsUpdate,
)
from fast_app.utils.common_utils import exclude_unset
from fast_app.utils.file_utils import upload_files
from fast_app.utils.logger import logger


async def get_contact_us() -> Dict[str, Any]:
    contact_us = await ContactUs.find_one(
        ContactUs.is_deleted == False
    )

    return {
        "message": "Contact Us retrieved successfully!",
        "data": contact_us.model_dump(by_alias=True, mode="json")
        if contact_us
        else None,
    }


async def create_contact_us(
    data: ContactUsCreate,
) -> Dict[str, Any]:

    # 🚫 Prevent multiple documents
    existing_policy = await ContactUs.find_one(
        ContactUs.is_deleted == False
    )
    if existing_policy:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contact Us already exists. Use update instead.",
        )

    image_path = ""

    # 🖼 Upload image
    if data.image:
        uploaded = await upload_files([data.image], "contact-us")
        image_path = uploaded[0].get("path", "")

    try:
        contact_us = ContactUs(
            content=data.content,
            image=image_path,
        )
        await contact_us.create()
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create Contact Us, please try again",
        )

    return {
        "message": "Contact Us created successfully",
        "data": contact_us.model_dump(by_alias=True, mode="json"),
    }



async def update_contact_us(
    data: ContactUsUpdate,
) -> Dict[str, Any]:

    contact_us = await ContactUs.find_one(
        ContactUs.is_deleted == False
    )

    update_data = data.model_dump(exclude_unset=True)

    # 🖼 Upload image
    if data.image:
        uploaded = await upload_files([data.image], "contact-us")
        update_data["image"] = uploaded[0].get("path", "")

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No data provided to update",
        )

    update_data["updated_at"] = datetime.utcnow()

    try:
        # 🔹 CREATE (if not exists)
        if not contact_us:
            contact_us = ContactUs(
                **update_data,
                is_deleted=False,
                created_at=datetime.utcnow(),
            )
            await contact_us.create()
            message = "Contact Us created successfully!"

        # 🔹 UPDATE (if exists)
        else:
            await contact_us.set(update_data)
            message = "Contact Us updated successfully!"

    except Exception as e:
        logger.error(str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to save Contact Us, please try again",
        )

    return {
        "message": message,
        "data": contact_us.model_dump(by_alias=True, mode="json"),
    }



async def remove_contact_us() -> Dict[str, Any]:
    contact_us = await ContactUs.find_one(
        ContactUs.is_deleted == False
    )

    if not contact_us:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contact Us does not exist",
        )

    await contact_us.set(
        {
            "is_deleted": True,
            "updated_at": datetime.utcnow(),
        }
    )

    return {
        "message": "Contact Us removed successfully!",
    }
