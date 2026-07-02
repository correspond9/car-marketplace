import hashlib
import secrets
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"
TOKEN_TYPE_ACCESS = "access"
TOKEN_TYPE_REFRESH = "refresh"


def hash_value(value: str) -> str:
    return pwd_context.hash(value)


def verify_hash(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def generate_otp() -> str:
    if settings.sms_provider == "mock":
        return "123456"
    upper = 10**settings.otp_length
    return str(secrets.randbelow(upper)).zfill(settings.otp_length)


def hash_otp(otp: str) -> str:
    return hashlib.sha256(otp.encode()).hexdigest()


def create_access_token(subject: str, role: str, extra: dict[str, Any] | None = None) -> str:
    expire = datetime.now(UTC) + timedelta(minutes=settings.access_token_expire_minutes)
    payload: dict[str, Any] = {
        "sub": subject,
        "role": role,
        "type": TOKEN_TYPE_ACCESS,
        "exp": expire,
    }
    if extra:
        payload.update(extra)
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)


def create_refresh_token(subject: str) -> tuple[str, str]:
    """Returns (token, jti) for storage in Redis."""
    jti = secrets.token_urlsafe(32)
    expire = datetime.now(UTC) + timedelta(days=settings.refresh_token_expire_days)
    payload = {
        "sub": subject,
        "type": TOKEN_TYPE_REFRESH,
        "jti": jti,
        "exp": expire,
    }
    token = jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)
    return token, jti


def decode_token(token: str) -> dict[str, Any]:
    return jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])


def verify_access_token(token: str) -> dict[str, Any]:
    try:
        payload = decode_token(token)
    except JWTError as exc:
        raise ValueError("Invalid token") from exc
    if payload.get("type") != TOKEN_TYPE_ACCESS:
        raise ValueError("Invalid token type")
    return payload


def verify_refresh_token(token: str) -> dict[str, Any]:
    try:
        payload = decode_token(token)
    except JWTError as exc:
        raise ValueError("Invalid refresh token") from exc
    if payload.get("type") != TOKEN_TYPE_REFRESH:
        raise ValueError("Invalid token type")
    return payload


def mask_registration_number(reg_number: str) -> str:
    """Mask last segment: MH12 AB 1234 -> MH12 AB ****"""
    parts = reg_number.strip().upper().split()
    if len(parts) < 2:
        return reg_number[:4] + " ****"
    parts[-1] = "****"
    return " ".join(parts)


def normalize_phone(phone: str) -> str:
    digits = "".join(c for c in phone if c.isdigit())
    if len(digits) == 10:
        return f"+91{digits}"
    if digits.startswith("91") and len(digits) == 12:
        return f"+{digits}"
    if phone.startswith("+") and len(digits) >= 10:
        return f"+{digits}"
    raise ValueError("Invalid Indian phone number")


def parse_uuid(value: str) -> UUID:
    return UUID(value)
