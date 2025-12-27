from datetime import datetime
from typing import Dict

from beanie import PydanticObjectId
from fastapi import HTTPException, Request, status

from fast_app.defaults.common_enums import StatusEnum, UserRole
from fast_app.modules.user.models.user_device_model import \
    UserDevice
from fast_app.modules.user.models.user_model import User
from fast_app.modules.user.schemas.user_schema import AdminProfileUpdateSchema
from fast_app.utils.crypto_utils import hash_password, verify_password
from fast_app.utils.email_utils import send_mail
from fast_app.utils.file_utils import upload_files
from fast_app.utils.jwt_utils import (create_access_token,
                                                         create_refresh_token,
                                                         verify_refresh_token)


import secrets
from datetime import timedelta


# -----------------------------------------------------
# REGISTER (ADMIN)
# -----------------------------------------------------
async def admin_register(data, request: Request) -> Dict:
    existing = await User.find_one(
        User.email == data.email.lower(),
        User.is_deleted == False,
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Admin already exists",
        )

    user = User(
        first_name=data.first_name,
        last_name=data.last_name,
        email=data.email,
        password=data.password,  # hashed via before_event
        role=UserRole.ADMIN,
        status=StatusEnum.ACTIVE,
    )

    await user.insert()

    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token(str(user.id))
    
    if user.id:
        await UserDevice(
            user_id=user.id,
            device_token=data.device_token,
            ip=request.client.host if request.client else "",
            access_token=access_token,
            refresh_token=refresh_token,
            role=user.role,
            last_active=datetime.utcnow(),
        ).insert()

    return {
        "user": user.model_dump(by_alias=True, mode="json"),
        "access_token": access_token,
        "refresh_token": refresh_token,
    }


# -----------------------------------------------------
# LOGIN (ADMIN)
# -----------------------------------------------------
async def admin_login(data, request: Request) -> dict:
    user = await User.find_one(
        User.email == data.email.lower(),
        User.is_deleted == False,
        User.role == UserRole.ADMIN,
    )

    if not user or not user.valid_password(data.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid credentials",
        )

    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token(str(user.id))

    device = await UserDevice.find_one(
        UserDevice.user_id == user.id,
        UserDevice.device_token == data.device_token,
        UserDevice.expired == False,
    )

    if device:
        await device.set(
            {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "last_active": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }
        )
    elif user.id:
        await UserDevice(
            user_id=user.id,
            device_token=data.device_token,
            # device_type=data.device_type,
            ip=request.client.host if request.client else "",
            access_token=access_token,
            refresh_token=refresh_token,
            role=user.role,
            last_active=datetime.utcnow(),
        ).insert()

    return {
        "user": user.model_dump(by_alias=True, mode="json"),
        "access_token": access_token,
        "refresh_token": refresh_token,
    }

# -----------------------------------------------------
# REFRESH TOKEN
# -----------------------------------------------------
async def refresh_token(refresh_token: str) -> dict:
    payload = verify_refresh_token(refresh_token)
    user_id = payload.get("sub")

    device = await UserDevice.find_one(
        UserDevice.refresh_token == refresh_token,
        UserDevice.expired == False,
    )

    if not device:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired",
        )

    access_token = create_access_token({"sub": user_id})

    await device.set(
        {
            "access_token": access_token,
            "updated_at": datetime.utcnow(),
        }
    )

    return {"access_token": access_token}



# -----------------------------------------------------
# LOGOUT
# -----------------------------------------------------
async def logout(access_token: str) -> None:
    device = await UserDevice.find_one(
        UserDevice.access_token == access_token,
        UserDevice.expired == False,
    )

    if device:
        await device.set(
            {
                "expired": True,
                "updated_at": datetime.utcnow(),
            }
        )




async def forgot_password(email: str):
    user = await User.find_one(
        User.email == email.lower(),
        User.is_deleted == False,
    )

    if not user:
        return  # silent fail (security)

    token = secrets.token_urlsafe(32)

    await user.set(
        {
            "reset_password_token": token,
            "reset_password_expires": datetime.utcnow() + timedelta(minutes=15),
        }
    )

    # TODO: send email with token
    await send_mail(email,"Reset password token", token)
    
    return token


async def reset_password(token: str, new_password: str):
    now = datetime.utcnow()

    user = await User.find_one(
        {
            "reset_password_token": token,
            "reset_password_expires": {"$gt": now},
        }
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )

    user.password = hash_password(new_password)
    user.reset_password_token = None
    user.reset_password_expires = None

    await user.save()

    await UserDevice.find(
        {"user_id": user.id, "expired": False}
    ).update_many(
        {
            "$set": {
                "expired": True,
                "updated_at": now,
            }
        }
    )


async def profile_details(user_id: PydanticObjectId):
    return await User.get(user_id)

async def update_profile(user_id: PydanticObjectId, user_data: AdminProfileUpdateSchema):
    update_data = user_data.model_dump(exclude_unset=True)

    if not update_data:
        return None

    user = await User.get(PydanticObjectId(user_id))
    if not user or user.is_deleted:
        return None
    
    profile_image_data = {}
    if user_data.profile_image:
        upload_result = await upload_files([user_data.profile_image], "profile-images")
        profile_image_data = upload_result[0]
    
    update_data["profile_image"]=profile_image_data.get("path","")
    update_data["updated_at"] = datetime.utcnow()
    update_data = {k: v for k, v in update_data.items() if v is not None}

    await user.set(update_data)

    return user.model_dump(by_alias=True, mode="json")