from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, status, Header
from typing import Optional

from fast_app.decorators.authenticator import login_required
from fast_app.decorators.catch_error import catch_error
from fast_app.defaults.common_enums import UserRole
from fast_app.modules.user.schemas.user_auth_schema import (
    BuyerProfileUpdateForm,
    SellerProfileUpdateForm,
    BuyerRegisterSchema,
    SellerRegisterSchema,
    LogoutSchema,
)
from fast_app.modules.user.schemas.user_auth_schema import SendOtpToUserPayload, VerifyLoginOtpPayload, VerifyRegistrationOtpPayload
from fast_app.modules.user.services import user_auth_service
from fast_app.modules.common.schemas.response_schema import (
    SuccessData,
    SuccessResponse,
)

router = APIRouter(prefix="/auth/user")

"""
send-otp -> verify-login-otp -> login -> logout
send-otp -> verify-registration-otp -> register -> logout

to resend otp, use send-otp api
"""

@router.post("/send-otp", response_model=SuccessData)
@catch_error
async def send_otp(request: Request, payload: SendOtpToUserPayload):
    data = await user_auth_service.send_otp(data=payload)
    return SuccessData(message="OTP send successfully.", data=data)


@router.post(
    "/verify-login-otp",
    response_model=SuccessData,
    status_code=status.HTTP_200_OK,
)
@catch_error
async def verify_login_otp(request: Request, payload: VerifyLoginOtpPayload):
    data = await user_auth_service.verify_login_otp(payload,request)
    return SuccessData(message="Successfully logged in.", data=data)


@router.post(
    "/verify-registration-otp",
    response_model=SuccessData,
    status_code=status.HTTP_200_OK,
)
@catch_error
async def verify_registration_otp(request: Request, payload: VerifyRegistrationOtpPayload):
    data = await user_auth_service.verify_registration_otp(payload)
    return SuccessData(message="OTP verified successfully.", data=data)

@router.post(
    "/buyer-register",
    response_model=SuccessData,
    status_code=status.HTTP_201_CREATED,
)
@catch_error
async def buyer_register(request: Request, form: BuyerRegisterSchema = Depends(BuyerRegisterSchema.as_form)):
    data = await user_auth_service.buyer_register(form,request)
    return SuccessData(message="successfully registered.", data=data)

@router.post(
    "/seller-register",
    response_model=SuccessData,
    status_code=status.HTTP_201_CREATED,
)
@catch_error
async def seller_register(request: Request, form: SellerRegisterSchema = Depends(SellerRegisterSchema.as_form)):
    data = await user_auth_service.seller_register(form,request)
    return SuccessData(message="successfully registered.", data=data)


@router.post("/logout", response_model=SuccessResponse)
@catch_error
@login_required(UserRole.END_USER, UserRole.VENDOR)
async def logout(request: Request):
    await user_auth_service.logout(request.state.access_token)
    return SuccessResponse(message="Successfully logged out.")

# -----------------------------------------------------
# PROFILE DETAILS
# -----------------------------------------------------
@router.get("/profile-details", response_model=SuccessData)
@catch_error
@login_required(UserRole.END_USER, UserRole.VENDOR)
async def profile_details(request: Request):
    user_data=await user_auth_service.profile_details(request.state.user.id)
    return SuccessData(message="Profile details fetched successfully.", data=user_data)


# -----------------------------------------------------
# UPDATE PROFILE
# -----------------------------------------------------
@router.patch("/buyer/update-profile", response_model=SuccessData)
@catch_error
@login_required(UserRole.END_USER, UserRole.VENDOR)
async def update_buyer_profile(
    request: Request,
    form: BuyerProfileUpdateForm = Depends(BuyerProfileUpdateForm.as_form),
):
    user = await user_auth_service.update_buyer_profile(
        request.state.user.id,
        form,
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found or no data to update."
        )

    return SuccessData(
        message="Profile updated successfully.",
        data=user
    )

@router.patch("/seller/update-profile", response_model=SuccessData)
@catch_error
@login_required(UserRole.END_USER, UserRole.VENDOR)
async def update_seller_profile(
    request: Request,
    form: SellerProfileUpdateForm = Depends(SellerProfileUpdateForm.as_form),
):
    user = await user_auth_service.update_seller_profile(
        request.state.user.id,
        form,
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found or no data to update."
        )

    return SuccessData(
        message="Profile updated successfully.",
        data=user
    )

