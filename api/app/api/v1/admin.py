import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db, require_roles
from app.api.schemas import (
    AdminRoleUpdate,
    AdminStatsOut,
    AuditLogListResponse,
    AuditLogOut,
    DealerStoreOut,
    DealerVerifyRequest,
)
from app.application.admin_service import AdminService
from app.application.audit import log_audit
from app.application.dealer_service import DealerError, DealerService
from app.domain.enums import UserRole
from app.infrastructure.database import UserModel

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/stats", response_model=AdminStatsOut)
async def admin_stats(
    db: Annotated[AsyncSession, Depends(get_db)],
    _admin: Annotated[UserModel, Depends(require_roles(UserRole.ADMIN))],
) -> AdminStatsOut:
    stats = await AdminService(db).stats()
    return AdminStatsOut(**stats)


@router.patch("/users/{user_id}/role", response_model=dict)
async def update_user_role(
    user_id: uuid.UUID,
    body: AdminRoleUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    admin: Annotated[UserModel, Depends(require_roles(UserRole.ADMIN))],
) -> dict:
    service = AdminService(db)
    try:
        user = await service.update_user_role(user_id, body.role)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "NOT_FOUND", "message": str(exc)}},
        ) from exc
    await log_audit(
        db,
        actor_id=admin.id,
        action="user.role_update",
        entity_type="user",
        entity_id=user.id,
        metadata={"role": body.role.value},
    )
    return {"id": str(user.id), "role": user.role.value}


@router.post("/dealer-stores/{store_id}/verify", response_model=DealerStoreOut)
async def verify_dealer_store(
    store_id: uuid.UUID,
    body: DealerVerifyRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    admin: Annotated[UserModel, Depends(require_roles(UserRole.ADMIN))],
) -> DealerStoreOut:
    service = DealerService(db)
    try:
        store = await service.verify_store(store_id, verified=body.verified)
    except DealerError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": exc.code, "message": exc.message}},
        ) from exc
    await log_audit(
        db,
        actor_id=admin.id,
        action="dealer.verify" if body.verified else "dealer.reject",
        entity_type="dealer_store",
        entity_id=store.id,
    )
    return DealerStoreOut.model_validate(store)


@router.get("/audit-logs", response_model=AuditLogListResponse)
async def list_audit_logs(
    db: Annotated[AsyncSession, Depends(get_db)],
    _admin: Annotated[UserModel, Depends(require_roles(UserRole.ADMIN))],
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
) -> AuditLogListResponse:
    items, total = await AdminService(db).list_audit_logs(page=page, limit=limit)
    return AuditLogListResponse(
        items=[AuditLogOut.model_validate(i) for i in items],
        total=total,
        page=page,
        limit=limit,
    )
