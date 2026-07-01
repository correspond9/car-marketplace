from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db
from app.api.schemas import HealthResponse
from app.infrastructure.redis_client import get_redis

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status="ok")


@router.get("/health/ready", response_model=HealthResponse)
async def readiness(db: Annotated[AsyncSession, Depends(get_db)]) -> HealthResponse:
    await db.execute(text("SELECT 1"))
    redis = await get_redis()
    await redis.ping()
    return HealthResponse(status="ready")
