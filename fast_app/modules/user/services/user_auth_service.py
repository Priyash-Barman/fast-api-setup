from datetime import datetime
from typing import Dict

from beanie import PydanticObjectId
from fastapi import HTTPException, Request, status

from config import ENV
from fast_app.defaults.common_enums import Env, OtpPurpose, StatusEnum, UserRole
from fast_app.modules.user.models.user_device_model import \
    UserDevice
from fast_app.modules.user.models.user_model import User
from fast_app.modules.user.models.user_otp_model import UserOtp
from fast_app.modules.user.schemas.user_auth_schema import BuyerProfileUpdateForm, BuyerRegisterSchema, SellerProfileUpdateForm, SellerRegisterSchema, UserProfileUpdateForm, UserRegisterSchema
from fast_app.modules.user.schemas.user_auth_schema import SendOtpToUserPayload, VerifyLoginOtpPayload, VerifyRegistrationOtpPayload
from fast_app.utils.common_utils import exclude_unset, generate_otp
from fast_app.utils.crypto_utils import hash_password
from fast_app.utils.email_utils import send_mail
from fast_app.utils.file_utils import upload_files
from fast_app.utils.jwt_utils import (create_access_token, create_refresh_token, create_registration_token, decode_token)
from beanie.operators import Or

from fast_app.utils.otp_utils import otp_expiry



async def send_otp(data: SendOtpToUserPayload):
    otp = generate_otp()

    if not data.email and not data.phone_number:
        raise HTTPException(400, "Email or phone number required")

    email = data.email.lower() if data.email else None
    phone = data.phone_number
    
    or_conditions = []
    if email:
        or_conditions.append(User.email == email)
    if phone:
        or_conditions.append(User.phone_number == phone)

    # Find user if exists (DO NOT CREATE)
    user = await User.find_one(
        Or(*or_conditions),
        User.role == data.role,
        User.is_deleted == False,
    )
    
    if data.purpose in [OtpPurpose.LOGIN, OtpPurpose.RESET_PASSWORD] and not user:
        raise HTTPException(404, "User not found")
    elif data.purpose == OtpPurpose.REGISTRATION and user:
        raise HTTPException(400, "User already exists")
    
    otp_conditions = []
    if email:
        otp_conditions.append(UserOtp.email == email)
    if phone:
        otp_conditions.append(UserOtp.phone_number == phone)

    # Find existing OTP
    otp_doc = await UserOtp.find_one(
        Or(*otp_conditions),
        UserOtp.purpose == data.purpose,
        UserOtp.verified == False,
        UserOtp.role == data.role,
    )

    # If OTP already exists → resend logic
    if otp_doc:
        if otp_doc.send_count >= otp_doc.max_send_count:
            raise HTTPException(
                status_code=429,
                detail="Maximum OTP send limit reached",
            )

        await otp_doc.set(
            {
                "otp": otp if ENV not in [Env.LOC, Env.DEV] else "1234",
                "expires_at": UserOtp.expiry(),
                "send_count": otp_doc.send_count + 1,
                "attempts": 0,  # reset attempts on resend
            }
        )

        return otp_doc.model_dump(by_alias=True, mode="json")

    # Create new OTP entry
    otp_doc = await UserOtp(
        user_id=user.id if user else None,
        email=email,
        phone_number=phone,
        purpose=data.purpose,
        otp= otp if ENV not in [Env.LOC, Env.DEV] else "1234",
        expires_at=UserOtp.expiry(),
        attempts=0,
        max_attempts=3,
        send_count=1,
        role=data.role,
        max_send_count=3,
    ).insert()
    
    # send OTP via email (if email provided) or SMS (if phone provided)

    return otp_doc.model_dump(by_alias=True, mode="json")


async def verify_registration_otp(
    data: VerifyRegistrationOtpPayload,
) -> Dict:
    if not data.email and not data.phone_number:
        raise HTTPException(400, "Email or phone number required")

    email = data.email.lower() if data.email else None
    phone = data.phone_number
    
    or_conditions = []
    if email:
        or_conditions.append(User.email == email)
    if phone:
        or_conditions.append(User.phone_number == phone)

    # ❌ Registration should fail if user already exists
    existing_user = await User.find_one(
        Or(*or_conditions),
        User.role == data.role,
        User.is_deleted == False,
    )

    if existing_user:
        raise HTTPException(400, "User already exists")

    otp_conditions = []
    if email:
        otp_conditions.append(UserOtp.email == email)
    if phone:
        otp_conditions.append(UserOtp.phone_number == phone)


    # 🔍 Find OTP entry
    otp_doc = await UserOtp.find_one(
        Or(*otp_conditions),
        UserOtp.purpose == OtpPurpose.REGISTRATION,
        UserOtp.verified == False,
        UserOtp.role == data.role,
    )

    if not otp_doc:
        raise HTTPException(400, "OTP not found")

    # ⏰ Expiry check
    if otp_doc.expires_at < datetime.utcnow():
        raise HTTPException(400, "OTP expired")

    # 🔐 Attempts exceeded
    if otp_doc.attempts >= otp_doc.max_attempts:
        raise HTTPException(429, "OTP attempts exceeded")

    # ❌ Invalid OTP
    if otp_doc.otp != data.otp:
        await otp_doc.set(
            {"attempts": otp_doc.attempts + 1}
        )
        raise HTTPException(400, "Invalid OTP")

    # ✅ Mark OTP verified
    await otp_doc.set(
        {
            "verified": True,
            "verified_at": datetime.utcnow(),
        }
    )

    # 🎟 Create registration token (no user yet)
    verification_token = create_registration_token(
        email if email else phone if phone else "",
        {
            "email": email,
            "phone_number": phone,
            "role": data.role,
        }
    )

    return {
        "verified": True,
        "verification_token": verification_token,
    }


async def buyer_register(data: BuyerRegisterSchema, request: Request) -> Dict:
    if not data.verification_token:
        raise HTTPException(400, "Verification token required")

    # 🔓 Decode registration token
    payload = decode_token(data.verification_token)
    token_data= payload.get("data", {})
    email = token_data.get("email")
    phone = token_data.get("phone_number")
    role = token_data.get("role")

    if role in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(400, "Admin registration not allowed")

    or_conditions = []
    if email:
        or_conditions.append(User.email == email)
    if phone:
        or_conditions.append(User.phone_number == phone)

    # 🚫 Prevent duplicate user
    existing = await User.find_one(
        Or(*or_conditions),
        User.role == role,
        User.is_deleted == False,
    )

    if existing:
        raise HTTPException(400, "User already exists")

    # 🖼 Upload profile image
    image_path = ""
    if data.profile_image:
        uploaded = await upload_files([data.profile_image], "profile-images")
        image_path = uploaded[0].get("path", "")

    # 👤 Create user (final step)
    user = await User(
        email=email,
        phone_number=phone,
        role=UserRole.END_USER,
        first_name=data.first_name,
        last_name=data.last_name,
        profile_image=image_path,
        geo_location=data.geo_location,
        status=StatusEnum.ACTIVE,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    ).insert()

    # 🔑 Tokens
    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token(str(user.id))

    # 📱 Device entry
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


async def seller_register(data: SellerRegisterSchema, request: Request) -> Dict:
    if not data.verification_token:
        raise HTTPException(400, "Verification token required")

    # 🔓 Decode registration token
    payload = decode_token(data.verification_token)
    token_data= payload.get("data", {})
    email = token_data.get("email")
    phone = token_data.get("phone_number")
    role = token_data.get("role")

    if role in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(400, "Admin registration not allowed")

    or_conditions = []
    if email:
        or_conditions.append(User.email == email)
    if phone:
        or_conditions.append(User.phone_number == phone)

    # 🚫 Prevent duplicate user
    existing = await User.find_one(
        Or(*or_conditions),
        User.role == role,
        User.is_deleted == False,
    )

    if existing:
        raise HTTPException(400, "User already exists")

    # 🖼 Upload profile image
    image_path = ""
    if data.profile_image:
        uploaded = await upload_files([data.profile_image], "profile-images")
        image_path = uploaded[0].get("path", "")


    # 👤 Create user (final step)
    user = await User(
        email=email,
        phone_number=phone,
        role=UserRole.VENDOR,
        first_name=data.first_name,
        last_name=data.last_name,
        profile_image=image_path,
        status=StatusEnum.ACTIVE,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        
        business_email=data.business_email,
        business_name=data.business_name,
        gst_number=data.gst_number,
        lisence_number=data.lisence_number,
        products=[PydanticObjectId(product_id) for product_id in data.products[0].split(",")] if data.products and len(data.products) else [],
    ).insert()

    # 🔑 Tokens
    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token(str(user.id))

    # 📱 Device entry
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


async def verify_login_otp(
    data: VerifyLoginOtpPayload,
    request: Request,
) -> Dict:
    if not data.email and not data.phone_number:
        raise HTTPException(400, "Email or phone number required")

    email = data.email.lower() if data.email else None
    phone = data.phone_number
    
    or_conditions = []
    if email:
        or_conditions.append(User.email == email)
    if phone:
        or_conditions.append(User.phone_number == phone)

    # 🔍 Find user (login requires existing user)
    user = await User.find_one(
        Or(*or_conditions),
        User.role == data.role,
        User.is_deleted == False,
    )

    if not user or not user.id:
        raise HTTPException(404, "User not found")
    
    otp_conditions = []
    if email:
        otp_conditions.append(UserOtp.email == email)
    if phone:
        otp_conditions.append(UserOtp.phone_number == phone)


    # 🔍 Find OTP
    otp_doc = await UserOtp.find_one(
        Or(*otp_conditions),
        UserOtp.purpose == OtpPurpose.LOGIN,
        UserOtp.verified == False,
        UserOtp.role == data.role,
    )

    if not otp_doc:
        raise HTTPException(400, "OTP not found")

    # ⏰ Expiry check
    if otp_doc.expires_at < datetime.utcnow():
        raise HTTPException(400, "OTP expired")

    # 🔐 Attempts exceeded
    if otp_doc.attempts >= otp_doc.max_attempts:
        raise HTTPException(429, "OTP attempts exceeded")

    # ❌ Invalid OTP
    if otp_doc.otp != data.otp:
        await otp_doc.set(
            {"attempts": otp_doc.attempts + 1}
        )
        raise HTTPException(400, "Invalid OTP")

    # ✅ Mark OTP verified
    await otp_doc.set(
        {
            "verified": True,
            "verified_at": datetime.utcnow(),
        }
    )

    # ✅ Update user login state
    await user.set(
        {
            "status": StatusEnum.ACTIVE,
            "is_online": True,
            "last_seen": datetime.utcnow(),
        }
    )

    # 🔑 Tokens
    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token(str(user.id))

    # 📱 Device tracking
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



async def profile_details(user_id: PydanticObjectId):
    return await User.get(user_id)

async def update_buyer_profile(user_id: PydanticObjectId, user_data: BuyerProfileUpdateForm):
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
    
    update_data["profile_image"]=profile_image_data.get("path",None)
    update_data["updated_at"] = datetime.utcnow()

    await user.set(exclude_unset(update_data))

    return user.model_dump(by_alias=True, mode="json")

async def update_seller_profile(user_id: PydanticObjectId, user_data: SellerProfileUpdateForm):
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
    
    update_data["profile_image"]=profile_image_data.get("path",None)
    update_data["updated_at"] = datetime.utcnow()
    update_data["products"]=[PydanticObjectId(pid) for pid in user_data.products] if user_data.products and user_data.products[0] else []
    print(update_data)
    await user.set(exclude_unset(update_data))

    return user.model_dump(by_alias=True, mode="json")


async def logout(access_token: str) -> None:
    # 🔓 Decode token to ensure it's valid
    payload = decode_token(access_token)
    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(401, "Invalid access token")

    # 🔍 Find active device session
    device = await UserDevice.find_one(
        UserDevice.access_token == access_token,
        UserDevice.expired == False,
    )

    if not device:
        return  # already logged out or token revoked

    # 🚫 Expire device session
    await device.set(
        {
            "expired": True,
            "updated_at": datetime.utcnow(),
        }
    )

    # 🕒 Update user's last seen
    user = await User.get(PydanticObjectId(user_id))
    if user:
        await user.set(
            {
                "is_online": False,
                "last_seen": datetime.utcnow(),
            }
        )
