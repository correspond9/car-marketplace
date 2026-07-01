import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database import AuditLogModel


async def log_audit(
    db: AsyncSession,
    *,
    actor_id: uuid.UUID,
    action: str,
    entity_type: str,
    entity_id: uuid.UUID,
    metadata: dict | None = None,
) -> AuditLogModel:
    entry = AuditLogModel(
        actor_id=actor_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        metadata_json=metadata,
    )
    db.add(entry)
    await db.flush()
    return entry
