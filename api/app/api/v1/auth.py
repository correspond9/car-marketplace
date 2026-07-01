from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, get_db
from app.api.schemas import (
    OTPRequest,
    OTPVerify,
    RefreshRequest,
    TokenResponse,
)
from app.application.auth_service import AuthError, AuthService
from app.infrastructure.database import UserModel
from app.infrastructure.sms import SMSService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/otp/request", status_code=status.HTTP_204_NO_CONTENT)
async def request_otp(
    body: OTPRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    service = AuthService(db, SMSService())
    try:
        await service.request_otp(body.phone)
    except AuthError as exc:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS
            if exc.code == "RATE_LIMITED"
            else status.HTTP_400_BAD_REQUEST,
            detail={"error": {"code": exc.code, "message": exc.message}},
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"error": {"code": "INVALID_PHONE", "message": str(exc)}},
        ) from exc


@router.post("/otp/verify", response_model=TokenResponse)
async def verify_otp(
    body: OTPVerify,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TokenResponse:
    service = AuthService(db, SMSService())
    try:
        _user, access, refresh = await service.verify_otp(body.phone, body.otp)
    except AuthError as exc:
        status_code = (
            status.HTTP_429_TOO_MANY_REQUESTS
            if exc.code == "RATE_LIMITED"
            else status.HTTP_401_UNAUTHORIZED
        )
        raise HTTPException(
            status_code=status_code,
            detail={"error": {"code": exc.code, "message": exc.message}},
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"error": {"code": "INVALID_PHONE", "message": str(exc)}},
        ) from exc
    return TokenResponse(access_token=access, refresh_token=refresh)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    body: RefreshRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TokenResponse:
    service = AuthService(db)
    try:
        access, new_refresh = await service.refresh_tokens(body.refresh_token)
    except AuthError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": {"code": exc.code, "message": exc.message}},
        ) from exc
    return TokenResponse(access_token=access, refresh_token=new_refresh)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(body: RefreshRequest, db: Annotated[AsyncSession, Depends(get_db)]) -> None:
    service = AuthService(db)
    await service.logout(body.refresh_token)


@router.delete("/account", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(
    user: Annotated[UserModel, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    service = AuthService(db)
    await service.delete_account(user)
