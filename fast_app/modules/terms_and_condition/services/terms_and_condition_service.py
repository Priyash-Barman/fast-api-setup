from typing import Any, Dict, List, Optional
from datetime import datetime

from fastapi import HTTPException, UploadFile, status
from beanie import PydanticObjectId

from fast_app.modules.terms_and_condition.models.terms_and_condition_model import (
    TermsAndCondition,
)
from fast_app.modules.terms_and_condition.schemas.terms_and_condition_schema import (
    TermsAndConditionCreate,
    TermsAndConditionUpdate,
)
from fast_app.utils.common_utils import exclude_unset
from fast_app.utils.file_utils import upload_files
from fast_app.utils.logger import logger


async def get_terms_and_condition() -> Dict[str, Any]:
    terms_and_condition = await TermsAndCondition.find_one(
        TermsAndCondition.is_deleted == False
    )

    return {
        "message": "Terms And Condition retrieved successfully!",
        "data": terms_and_condition.model_dump(by_alias=True, mode="json")
        if terms_and_condition
        else None,
    }


async def create_terms_and_condition(
    data: TermsAndConditionCreate,
) -> Dict[str, Any]:

    # 🚫 Prevent multiple documents
    existing_policy = await TermsAndCondition.find_one(
        TermsAndCondition.is_deleted == False
    )
    if existing_policy:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Terms And Condition already exists. Use update instead.",
        )

    image_path = ""

    # 🖼 Upload image
    if data.image:
        uploaded = await upload_files([data.image], "terms-and-condition")
        image_path = uploaded[0].get("path", "")

    try:
        terms_and_condition = TermsAndCondition(
            content=data.content,
            image=image_path,
        )
        await terms_and_condition.create()
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create Terms And Condition, please try again",
        )

    return {
        "message": "Terms And Condition created successfully",
        "data": terms_and_condition.model_dump(by_alias=True, mode="json"),
    }



async def update_terms_and_condition(
    data: TermsAndConditionUpdate,
) -> Dict[str, Any]:

    terms_and_condition = await TermsAndCondition.find_one(
        TermsAndCondition.is_deleted == False
    )

    update_data = data.model_dump(exclude_unset=True)

    # 🖼 Upload image
    if data.image:
        uploaded = await upload_files([data.image], "terms-and-condition")
        update_data["image"] = uploaded[0].get("path", "")

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No data provided to update",
        )

    update_data["updated_at"] = datetime.utcnow()

    try:
        # 🔹 CREATE (if not exists)
        if not terms_and_condition:
            terms_and_condition = TermsAndCondition(
                **update_data,
                is_deleted=False,
                created_at=datetime.utcnow(),
            )
            await terms_and_condition.create()
            message = "Terms And Condition created successfully!"

        # 🔹 UPDATE (if exists)
        else:
            await terms_and_condition.set(update_data)
            message = "Terms And Condition updated successfully!"

    except Exception as e:
        logger.error(str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to save Terms And Condition, please try again",
        )

    return {
        "message": message,
        "data": terms_and_condition.model_dump(by_alias=True, mode="json"),
    }



async def remove_terms_and_condition() -> Dict[str, Any]:
    terms_and_condition = await TermsAndCondition.find_one(
        TermsAndCondition.is_deleted == False
    )

    if not terms_and_condition:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Terms And Condition does not exist",
        )

    await terms_and_condition.set(
        {
            "is_deleted": True,
            "updated_at": datetime.utcnow(),
        }
    )

    return {
        "message": "Terms And Condition removed successfully!",
    }
