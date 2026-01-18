from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, status, Header
from typing import Optional

from fast_app.decorators.authenticator import login_required
from fast_app.decorators.catch_error import catch_error
from fast_app.defaults.common_enums import UserRole
from fast_app.modules.user.schemas.admin_auth_schema import (
    AdminChangePasswordSchema,
    AdminLoginSchema,
    AdminProfileUpdateForm,
    AdminRegisterSchema,
    RefreshTokenSchema,
    LogoutSchema,
    ForgotPasswordSchema,
    ResetPasswordSchema,
)
from fast_app.modules.user.schemas.user_schema import AdminProfileUpdateSchema
from fast_app.modules.user.services import admin_auth_service
from fast_app.modules.common.schemas.response_schema import (
    SuccessData,
    SuccessResponse,
)

router = APIRouter(prefix="/auth")


# -----------------------------------------------------
# ADMIN LOGIN
# -----------------------------------------------------
@router.post("/admin/login", response_model=SuccessData)
@catch_error
async def admin_login(request: Request, payload: AdminLoginSchema):
    data = await admin_auth_service.admin_login(
        data=payload,
        request=request,
    )
    return SuccessData(message="Successfully logged in.", data=data)


# -----------------------------------------------------
# ADMIN REGISTER
# -----------------------------------------------------
@router.post(
    "/admin/register",
    response_model=SuccessData,
    status_code=status.HTTP_201_CREATED,
)
@catch_error
async def admin_register(request: Request, payload: AdminRegisterSchema):
    data = await admin_auth_service.admin_register(payload,request)
    return SuccessData(message="Admin registered successfully.", data=data)


# -----------------------------------------------------
# REFRESH TOKEN
# -----------------------------------------------------
@router.post("/admin/refresh-token", response_model=SuccessData)
@catch_error
async def refresh_token(request: Request, payload: RefreshTokenSchema):
    data = await admin_auth_service.refresh_token(payload.refresh_token)
    return SuccessData(message="Token refreshed successfully.", data=data)


# -----------------------------------------------------
# LOGOUT (EXPIRE DEVICE SESSION)
# -----------------------------------------------------
@router.post("/admin/logout", response_model=SuccessResponse)
@catch_error
@login_required(UserRole.ADMIN)
async def logout(request: Request):
    await admin_auth_service.logout(request.state.access_token)
    return SuccessResponse(message="Successfully logged out.")


# -----------------------------------------------------
# FORGOT PASSWORD
# -----------------------------------------------------
@router.post("/admin/forgot-password", response_model=SuccessResponse)
@catch_error
async def forgot_password(request: Request, payload: ForgotPasswordSchema):
    await admin_auth_service.forgot_password(payload.reset_url, payload.email)
    return SuccessResponse(
        message="If the email exists, a reset link has been sent."
    )


# -----------------------------------------------------
# RESET PASSWORD
# -----------------------------------------------------
@router.post("/admin/reset-password", response_model=SuccessResponse)
@catch_error
async def reset_password(request: Request, payload: ResetPasswordSchema):
    await admin_auth_service.reset_password(
        token=payload.token,
        new_password=payload.new_password,
    )
    return SuccessResponse(message="Password reset successfully.")


# -----------------------------------------------------
# PROFILE DETAILS
# -----------------------------------------------------
@router.get("/admin/profile-details", response_model=SuccessData)
@catch_error
@login_required(UserRole.ADMIN)
async def profile_details(request: Request):
    user_data=await admin_auth_service.profile_details(request.state.user.id)
    return SuccessData(message="Profile details fetched successfully.", data=user_data)


# -----------------------------------------------------
# UPDATE PROFILE
# -----------------------------------------------------
@router.patch("/admin/update-profile", response_model=SuccessData)
@catch_error
@login_required(UserRole.ADMIN)
async def update_profile(
    request: Request,
    form: AdminProfileUpdateForm = Depends(AdminProfileUpdateForm.as_form),
):
    user = await admin_auth_service.update_profile(
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


# -----------------------------------------------------
# CHANGE PASSWORD
# -----------------------------------------------------
@router.patch("/admin/change-password", response_model=SuccessData)
@catch_error
@login_required(UserRole.ADMIN)
async def change_password(
    request: Request,
    data: AdminChangePasswordSchema,
):
    user = await admin_auth_service.change_password(
        request.state.user.id,
        data,
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found or no data to update."
        )

    return SuccessData(
        message="Password changed successfully.",
        data=user
    )

