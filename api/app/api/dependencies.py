import uuid
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.auth_service import AuthService
from app.core.security import verify_access_token
from app.domain.enums import UserRole
from app.infrastructure.database import UserModel, get_db_session

security_scheme = HTTPBearer(auto_error=False)


async def get_db(db: Annotated[AsyncSession, Depends(get_db_session)]) -> AsyncSession:
    return db


async def get_current_user_optional(
    db: Annotated[AsyncSession, Depends(get_db)],
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security_scheme)],
) -> UserModel | None:
    if not credentials:
        return None
    try:
        payload = verify_access_token(credentials.credentials)
        user_id = uuid.UUID(payload["sub"])
    except (ValueError, KeyError):
        return None
    return await AuthService.get_user_by_id(db, user_id)


async def get_current_user(
    user: Annotated[UserModel | None, Depends(get_current_user_optional)],
) -> UserModel:
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": {"code": "UNAUTHORIZED", "message": "Authentication required"}},
        )
    return user


def require_roles(*roles: UserRole):
    async def checker(user: Annotated[UserModel, Depends(get_current_user)]) -> UserModel:
        if user.role == UserRole.ADMIN:
            return user
        if user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"error": {"code": "FORBIDDEN", "message": "Insufficient permissions"}},
            )
        return user

    return checker
