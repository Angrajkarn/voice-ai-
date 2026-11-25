# Audit Service - Handles audit logging

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Any
from datetime import datetime
from uuid import UUID
import json


class AuditService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def log(
        self,
        action: str,
        entity_type: str,
        entity_id: str,
        organization_id: UUID,
        user_id: Optional[UUID] = None,
        old_data: Optional[dict] = None,
        new_data: Optional[dict] = None,
        metadata: Optional[dict] = None,
    ) -> None:
        from app.models.audit_log import AuditLog

        audit_log = AuditLog(
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            organization_id=organization_id,
            user_id=user_id,
            old_data=old_data,
            new_data=new_data,
            metadata_json=metadata or {},
        )
        self.db.add(audit_log)
        await self.db.commit()

    async def log_create(
        self,
        entity_type: str,
        entity_id: str,
        organization_id: UUID,
        user_id: Optional[UUID] = None,
        new_data: Optional[dict] = None,
        metadata: Optional[dict] = None,
    ) -> None:
        await self.log(
            action="CREATE",
            entity_type=entity_type,
            entity_id=entity_id,
            organization_id=organization_id,
            user_id=user_id,
            new_data=new_data,
            metadata=metadata,
        )

    async def log_update(
        self,
        entity_type: str,
        entity_id: str,
        organization_id: UUID,
        user_id: Optional[UUID] = None,
        old_data: Optional[dict] = None,
        new_data: Optional[dict] = None,
        metadata: Optional[dict] = None,
    ) -> None:
        await self.log(
            action="UPDATE",
            entity_type=entity_type,
            entity_id=entity_id,
            organization_id=organization_id,
            user_id=user_id,
            old_data=old_data,
            new_data=new_data,
            metadata=metadata,
        )

    async def log_delete(
        self,
        entity_type: str,
        entity_id: str,
        organization_id: UUID,
        user_id: Optional[UUID] = None,
        old_data: Optional[dict] = None,
        metadata: Optional[dict] = None,
    ) -> None:
        await self.log(
            action="DELETE",
            entity_type=entity_type,
            entity_id=entity_id,
            organization_id=organization_id,
            user_id=user_id,
            old_data=old_data,
            metadata=metadata,
        )

    async def log_call_event(
        self,
        call_id: UUID,
        event: str,
        organization_id: UUID,
        user_id: Optional[UUID] = None,
        metadata: Optional[dict] = None,
    ) -> None:
        await self.log(
            action=event,
            entity_type="Call",
            entity_id=str(call_id),
            organization_id=organization_id,
            user_id=user_id,
            metadata=metadata,
        )

    async def log_sync_event(
        self,
        integration_id: UUID,
        entity_type: str,
        entity_id: str,
        organization_id: UUID,
        status: str,
        error: Optional[str] = None,
    ) -> None:
        await self.log(
            action="SYNC",
            entity_type=entity_type,
            entity_id=entity_id,
            organization_id=organization_id,
            metadata={
                "integration_id": str(integration_id),
                "sync_status": status,
                "error": error,
            },
        )

    async def get_audit_logs(
        self,
        organization_id: UUID,
        page: int = 1,
        page_size: int = 50,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        user_id: Optional[UUID] = None,
        action: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> tuple[List[dict], int]:
        from app.models.audit_log import AuditLog

        query = select(AuditLog).where(AuditLog.organization_id == organization_id)

        if entity_type:
            query = query.where(AuditLog.entity_type == entity_type)

        if entity_id:
            query = query.where(AuditLog.entity_id == entity_id)

        if user_id:
            query = query.where(AuditLog.user_id == user_id)

        if action:
            query = query.where(AuditLog.action == action)

        if date_from:
            query = query.where(AuditLog.created_at >= date_from)

        if date_to:
            query = query.where(AuditLog.created_at <= date_to)

        count_query = select(func.count()).select_from(query.subquery())
        total = await self.db.scalar(count_query) or 0

        query = query.order_by(AuditLog.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await self.db.execute(query)
        logs = result.scalars().all()

        return [
            {
                "id": log.id,
                "action": log.action,
                "entity_type": log.entity_type,
                "entity_id": log.entity_id,
                "user_id": log.user_id,
                "old_data": log.old_data,
                "new_data": log.new_data,
                "metadata": log.metadata_json,
                "created_at": log.created_at.isoformat(),
            }
            for log in logs
        ], total