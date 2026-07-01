import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    generate_otp,
    hash_otp,
    normalize_phone,
)
from app.domain.enums import UserRole
from app.infrastructure.database import UserModel
from app.infrastructure.redis_client import RateLimiter, get_redis
from app.infrastructure.sms import SMSService


class AuthError(Exception):
    def __init__(self, message: str, code: str = "AUTH_ERROR"):
        self.message = message
        self.code = code
        super().__init__(message)


class AuthService:
    OTP_KEY_PREFIX = "otp"
    REFRESH_KEY_PREFIX = "refresh"

    def __init__(self, db: AsyncSession, sms: SMSService | None = None):
        self.db = db
        self.sms = sms or SMSService()

    async def request_otp(self, phone_raw: str) -> None:
        phone = normalize_phone(phone_raw)
        redis = await get_redis()
        limiter = RateLimiter(redis, "rate:otp_request", limit=3, window_seconds=900)
        if not await limiter.is_allowed(phone):
            raise AuthError("Too many OTP requests. Try again later.", "RATE_LIMITED")

        otp = generate_otp()
        otp_hash = hash_otp(otp)
        key = f"{self.OTP_KEY_PREFIX}:{phone}"
        await redis.setex(key, settings.otp_expire_minutes * 60, otp_hash)
        await self.sms.send_otp(phone, otp)

    async def verify_otp(self, phone_raw: str, otp: str) -> tuple[UserModel, str, str]:
        phone = normalize_phone(phone_raw)
        redis = await get_redis()
        limiter = RateLimiter(redis, "rate:otp_verify", limit=5, window_seconds=900)
        if not await limiter.is_allowed(phone):
            raise AuthError("Too many verification attempts.", "RATE_LIMITED")

        key = f"{self.OTP_KEY_PREFIX}:{phone}"
        stored_hash = await redis.get(key)
        if not stored_hash or stored_hash != hash_otp(otp):
            raise AuthError("Invalid or expired OTP.", "INVALID_OTP")

        await redis.delete(key)
        user = await self._get_or_create_user(phone)
        user.phone_verified = True
        await self.db.flush()

        access = create_access_token(str(user.id), user.role.value)
        refresh, jti = create_refresh_token(str(user.id))
        await redis.setex(
            f"{self.REFRESH_KEY_PREFIX}:{jti}",
            settings.refresh_token_expire_days * 86400,
            str(user.id),
        )
        return user, access, refresh

    async def refresh_tokens(self, refresh_token: str) -> tuple[str, str]:
        from app.core.security import verify_refresh_token

        try:
            payload = verify_refresh_token(refresh_token)
        except ValueError as exc:
            raise AuthError("Invalid refresh token.", "INVALID_TOKEN") from exc

        jti = payload.get("jti")
        user_id = payload.get("sub")
        if not jti or not user_id:
            raise AuthError("Invalid refresh token.", "INVALID_TOKEN")

        redis = await get_redis()
        stored_user = await redis.get(f"{self.REFRESH_KEY_PREFIX}:{jti}")
        if not stored_user or stored_user != user_id:
            raise AuthError("Refresh token revoked.", "INVALID_TOKEN")

        await redis.delete(f"{self.REFRESH_KEY_PREFIX}:{jti}")

        user = await self.db.get(UserModel, uuid.UUID(user_id))
        if not user or user.deleted_at:
            raise AuthError("User not found.", "USER_NOT_FOUND")

        access = create_access_token(str(user.id), user.role.value)
        new_refresh, new_jti = create_refresh_token(str(user.id))
        await redis.setex(
            f"{self.REFRESH_KEY_PREFIX}:{new_jti}",
            settings.refresh_token_expire_days * 86400,
            str(user.id),
        )
        return access, new_refresh

    async def logout(self, refresh_token: str) -> None:
        from app.core.security import verify_refresh_token

        try:
            payload = verify_refresh_token(refresh_token)
            jti = payload.get("jti")
            if jti:
                redis = await get_redis()
                await redis.delete(f"{self.REFRESH_KEY_PREFIX}:{jti}")
        except ValueError:
            pass

    async def delete_account(self, user: UserModel) -> None:
        user.deleted_at = datetime.now(UTC)
        user.phone = f"deleted_{user.id}@carmarket.local"
        user.email = None
        user.display_name = "Deleted User"
        await self.db.flush()

    async def _get_or_create_user(self, phone: str) -> UserModel:
        result = await self.db.execute(
            select(UserModel).where(UserModel.phone == phone, UserModel.deleted_at.is_(None))
        )
        user = result.scalar_one_or_none()
        if user:
            return user
        user = UserModel(phone=phone, role=UserRole.USER)
        self.db.add(user)
        await self.db.flush()
        return user

    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: uuid.UUID) -> UserModel | None:
        result = await db.execute(
            select(UserModel).where(UserModel.id == user_id, UserModel.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()
