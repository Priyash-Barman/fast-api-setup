from typing import Any, Dict, List, Optional
from datetime import datetime

from fastapi import HTTPException, UploadFile, status
from beanie import PydanticObjectId

from fast_app.modules.privacy_policy.models.privacy_policy_model import (
    PrivacyPolicy,
)
from fast_app.modules.privacy_policy.schemas.privacy_policy_schema import (
    PrivacyPolicyCreate,
    PrivacyPolicyUpdate,
)
from fast_app.utils.common_utils import exclude_unset
from fast_app.utils.file_utils import upload_files
from fast_app.utils.logger import logger


async def get_privacy_policy() -> Dict[str, Any]:
    privacy_policy = await PrivacyPolicy.find_one(
        PrivacyPolicy.is_deleted == False
    )

    return {
        "message": "Privacy Policy retrieved successfully!",
        "data": privacy_policy.model_dump(by_alias=True, mode="json")
        if privacy_policy
        else None,
    }


async def create_privacy_policy(
    data: PrivacyPolicyCreate,
) -> Dict[str, Any]:

    # 🚫 Prevent multiple documents
    existing_policy = await PrivacyPolicy.find_one(
        PrivacyPolicy.is_deleted == False
    )
    if existing_policy:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Privacy Policy already exists. Use update instead.",
        )

    image_path = ""

    # 🖼 Upload image
    if data.image:
        uploaded = await upload_files([data.image], "privacy-policy")
        image_path = uploaded[0].get("path", "")

    try:
        privacy_policy = PrivacyPolicy(
            content=data.content,
            image=image_path,
        )
        await privacy_policy.create()
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create Privacy Policy, please try again",
        )

    return {
        "message": "Privacy Policy created successfully",
        "data": privacy_policy.model_dump(by_alias=True, mode="json"),
    }



async def update_privacy_policy(
    data: PrivacyPolicyUpdate,
) -> Dict[str, Any]:

    privacy_policy = await PrivacyPolicy.find_one(
        PrivacyPolicy.is_deleted == False
    )

    update_data = data.model_dump(exclude_unset=True)

    # 🖼 Upload image
    if data.image:
        uploaded = await upload_files([data.image], "privacy-policy")
        update_data["image"] = uploaded[0].get("path", "")

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No data provided to update",
        )

    update_data["updated_at"] = datetime.utcnow()

    try:
        # 🔹 CREATE (if not exists)
        if not privacy_policy:
            privacy_policy = PrivacyPolicy(
                **update_data,
                is_deleted=False,
                created_at=datetime.utcnow(),
            )
            await privacy_policy.create()

            message = "Privacy Policy created successfully!"

        # 🔹 UPDATE (if exists)
        else:
            await privacy_policy.set(update_data)
            message = "Privacy Policy updated successfully!"

    except Exception as e:
        logger.error(str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to save Privacy Policy, please try again",
        )

    return {
        "message": message,
        "data": privacy_policy.model_dump(by_alias=True, mode="json"),
    }




async def remove_privacy_policy() -> Dict[str, Any]:
    privacy_policy = await PrivacyPolicy.find_one(
        PrivacyPolicy.is_deleted == False
    )

    if not privacy_policy:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Privacy Policy does not exist",
        )

    await privacy_policy.set(
        {
            "is_deleted": True,
            "updated_at": datetime.utcnow(),
        }
    )

    return {
        "message": "Privacy Policy removed successfully!",
    }
