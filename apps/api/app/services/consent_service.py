# Consent Service - Manages consent records

from datetime import datetime
from uuid import UUID

from app.models.consent_record import ConsentRecord
from app.models.enums import ConsentMethod, ConsentStatus
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession


class ConsentService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def record_consent(
        self,
        phone: str,
        status: str,
        method: str,
        organization_id: UUID,
        campaign_id: UUID | None = None,
        customer_id: UUID | None = None,
        proof_url: str | None = None,
        proof_expires_at: datetime | None = None,
    ) -> ConsentRecord:
        from app.services.suppression_service import SuppressionService
        suppression_service = SuppressionService(self.db)
        phone = suppression_service._normalize_phone(phone)

        # Check for existing consent record
        existing = await self.db.scalar(
            select(ConsentRecord).where(
                and_(
                    ConsentRecord.organization_id == organization_id,
                    ConsentRecord.phone == phone,
                )
            ).order_by(ConsentRecord.created_at.desc())
        )

        if existing:
            # Update existing
            existing.status = ConsentStatus(status)
            existing.method = ConsentMethod(method)
            existing.proof_url = proof_url
            existing.proof_expires_at = proof_expires_at
            existing.campaign_id = campaign_id
            existing.customer_id = customer_id
            if status == "GRANTED":
                existing.granted_at = datetime.utcnow()
                existing.revoked_at = None
            elif status == "REVOKED":
                existing.revoked_at = datetime.utcnow()
            await self.db.commit()
            await self.db.refresh(existing)
            return existing

        consent = ConsentRecord(
            phone=phone,
            status=ConsentStatus(status),
            method=ConsentMethod(method),
            proof_url=proof_url,
            proof_expires_at=proof_expires_at,
            campaign_id=campaign_id,
            customer_id=customer_id,
            organization_id=organization_id,
            granted_at=datetime.utcnow() if status == "GRANTED" else None,
        )
        self.db.add(consent)
        await self.db.commit()
        await self.db.refresh(consent)
        return consent

    async def revoke_consent(self, consent_id: UUID, organization_id: UUID) -> ConsentRecord | None:
        consent = await self.db.scalar(
            select(ConsentRecord).where(
                and_(
                    ConsentRecord.id == consent_id,
                    ConsentRecord.organization_id == organization_id,
                )
            )
        )
        if not consent:
            return None

        consent.status = ConsentStatus.REVOKED
        consent.revoked_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(consent)
        return consent

    async def get_consent_status(self, phone: str, organization_id: UUID) -> ConsentStatus | None:
        from app.services.suppression_service import SuppressionService
        suppression_service = SuppressionService(self.db)
        phone = suppression_service._normalize_phone(phone)

        consent = await self.db.scalar(
            select(ConsentRecord).where(
                and_(
                    ConsentRecord.organization_id == organization_id,
                    ConsentRecord.phone == phone,
                )
            ).order_by(ConsentRecord.created_at.desc())
        )
        return consent.status if consent else None

    async def list_consents(
        self,
        organization_id: UUID,
        page: int = 1,
        page_size: int = 20,
        status: str | None = None,
    ) -> tuple[list[ConsentRecord], int]:
        query = select(ConsentRecord).where(ConsentRecord.organization_id == organization_id)

        if status:
            query = query.where(ConsentRecord.status == status)

        from sqlalchemy import func
        count_query = select(func.count()).select_from(query.subquery())
        total = await self.db.scalar(count_query) or 0

        query = query.order_by(ConsentRecord.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await self.db.execute(query)
        consents = result.scalars().all()

        return list(consents), total