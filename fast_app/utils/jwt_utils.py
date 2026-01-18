# utils/jwt_utils.py
from datetime import datetime, timedelta
from typing import Any, Optional, Dict
import jwt
from fastapi import HTTPException, status
from fast_app.utils.logger import logger

from config import (
    JWT_ACCESS_SECRET_KEY,
    JWT_REFRESH_SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS,
)


# -------------------------------------------------
# ACCESS TOKEN
# -------------------------------------------------
def create_access_token(
    data: Dict,
    expires_delta: Optional[timedelta] = None,
) -> str:
    to_encode = data.copy()

    expire = datetime.utcnow() + (
        expires_delta
        if expires_delta
        else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    to_encode.update({
        "exp": expire,
        "type": "access",
    })

    return jwt.encode(to_encode, JWT_ACCESS_SECRET_KEY, algorithm=ALGORITHM)


def verify_access_token(token: str):
    try:
        payload = jwt.decode(
            token,
            JWT_ACCESS_SECRET_KEY,
            algorithms=[ALGORITHM],
        )
        if payload.get("type") != "access":
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid access token")
        return payload
    except jwt.ExpiredSignatureError as e:
        logger.error(e.with_traceback)
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Access token expired")
    except jwt.InvalidTokenError as e:
        logger.error(e.with_traceback)
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid access token")


# -------------------------------------------------
# REFRESH TOKEN
# -------------------------------------------------
def create_refresh_token(user_id: str) -> str:
    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "exp": datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    }
    return jwt.encode(payload, JWT_REFRESH_SECRET_KEY, algorithm=ALGORITHM)


def verify_refresh_token(token: str):
    try:
        payload = jwt.decode(
            token,
            JWT_REFRESH_SECRET_KEY,
            algorithms=[ALGORITHM],
        )
        if payload.get("type") != "refresh":
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid refresh token")
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Refresh token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid refresh token")

def create_registration_token(sub: str, data: Dict[str, Any]) -> str:
    return create_access_token(
        data={
            "sub": sub,
            "data": data,
            "type": "REG_VERIFICATION",
        },
        expires_delta=timedelta(minutes=5),  # 5 minutes
    )


def decode_token(token: str):
    """
    Generic JWT decoder.
    Works for access, refresh, registration, or custom tokens.

    :param token: JWT string
    :return: decoded payload
    """
    try:
        payload = jwt.decode(
            token,
            JWT_ACCESS_SECRET_KEY,
            algorithms=[ALGORITHM],
        )
        return payload

    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )