# Suppression Service - Manages Do Not Call / Suppression lists

from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime
from uuid import UUID
import csv
import io

from app.models.suppression_list import SuppressionList
from app.models.customer import Customer
from app.models.enums import SuppressionReason, SuppressionSource
from app.core.config import settings


class SuppressionService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def add_to_suppression(
        self,
        phone: str,
        reason: str,
        organization_id: UUID,
        customer_id: Optional[UUID] = None,
        campaign_id: Optional[UUID] = None,
        expires_at: Optional[datetime] = None,
        added_by: str = "system",
    ) -> SuppressionList:
        # Normalize phone
        phone = self._normalize_phone(phone)

        # Check if already exists
        existing = await self.db.scalar(
            select(SuppressionList).where(
                and_(
                    SuppressionList.organization_id == organization_id,
                    SuppressionList.phone == phone,
                    SuppressionList.is_active == True,
                )
            )
        )

        if existing:
            # Update existing
            existing.reason = SuppressionReason(reason)
            existing.source = SuppressionSource.MANUAL if reason == "MANUAL" else SuppressionSource.CAMPAIGN
            existing.campaign_id = campaign_id
            existing.expires_at = expires_at
            existing.added_by = added_by
            await self.db.commit()
            await self.db.refresh(existing)
            return existing

        suppression = SuppressionList(
            phone=phone,
            reason=SuppressionReason(reason),
            source=SuppressionSource.MANUAL if reason == "MANUAL" else SuppressionSource.CAMPAIGN,
            campaign_id=campaign_id,
            organization_id=organization_id,
            customer_id=customer_id,
            expires_at=expires_at,
            is_active=True,
            added_by=added_by,
        )
        self.db.add(suppression)
        await self.db.commit()
        await self.db.refresh(suppression)
        return suppression

    async def remove_from_suppression(self, suppression_id: UUID, organization_id: UUID) -> bool:
        suppression = await self.db.scalar(
            select(SuppressionList).where(
                and_(
                    SuppressionList.id == suppression_id,
                    SuppressionList.organization_id == organization_id,
                )
            )
        )
        if not suppression:
            return False

        suppression.is_active = False
        await self.db.commit()
        return True

    async def is_suppressed(self, phone: str, organization_id: UUID) -> bool:
        phone = self._normalize_phone(phone)
        suppression = await self.db.scalar(
            select(SuppressionList).where(
                and_(
                    SuppressionList.organization_id == organization_id,
                    SuppressionList.phone == phone,
                    SuppressionList.is_active == True,
                    or_(
                        SuppressionList.expires_at.is_(None),
                        SuppressionList.expires_at > datetime.utcnow(),
                    ),
                )
            )
        )
        return suppression is not None

    async def list_suppressions(
        self,
        organization_id: UUID,
        page: int = 1,
        page_size: int = 20,
        active_only: bool = True,
    ) -> tuple[List[SuppressionList], int]:
        query = select(SuppressionList).where(SuppressionList.organization_id == organization_id)

        if active_only:
            query = query.where(SuppressionList.is_active == True)

        # Count total
        from sqlalchemy import func
        count_query = select(func.count()).select_from(query.subquery())
        total = await self.db.scalar(count_query) or 0

        # Pagination
        query = query.order_by(SuppressionList.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await self.db.execute(query)
        suppressions = result.scalars().all()

        return list(suppressions), total

    async def bulk_import(
        self,
        file_content: bytes,
        organization_id: UUID,
        reason: str = "IMPORT",
        source: str = "IMPORT",
    ) -> Dict[str, Any]:
        text = file_content.decode("utf-8")
        reader = csv.DictReader(io.StringIO(text))

        added = 0
        skipped = 0
        errors = []

        for idx, row in enumerate(reader):
            phone = row.get("phone") or row.get("phone_number") or row.get("Phone")
            if not phone:
                errors.append({"row": idx + 1, "error": "No phone number found"})
                continue

            phone = self._normalize_phone(phone)

            existing = await self.db.scalar(
                select(SuppressionList).where(
                    and_(
                        SuppressionList.organization_id == organization_id,
                        SuppressionList.phone == phone,
                        SuppressionList.is_active == True,
                    )
                )
            )

            if existing:
                skipped += 1
                continue

            suppression = SuppressionList(
                phone=phone,
                reason=SuppressionReason(reason) if reason in [r.value for r in SuppressionReason] else SuppressionReason.MANUAL,
                source=SuppressionSource(source) if source in [s.value for s in SuppressionSource] else SuppressionSource.IMPORT,
                organization_id=organization_id,
                is_active=True,
                added_by="import",
            )
            self.db.add(suppression)
            added += 1

        await self.db.commit()
        return {"added": added, "skipped": skipped, "errors": errors}

    async def export_suppressions(self, organization_id: UUID) -> bytes:
        suppressions, _ = await self.list_suppressions(organization_id, page=1, page_size=10000, active_only=True)

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Phone", "Reason", "Source", "Campaign ID", "Expires At", "Added By", "Created At"])

        for s in suppressions:
            writer.writerow([
                s.phone, s.reason.value, s.source.value,
                str(s.campaign_id) if s.campaign_id else "",
                s.expires_at.isoformat() if s.expires_at else "",
                s.added_by, s.created_at.isoformat(),
            ])

        return output.getvalue().encode("utf-8")

    def _normalize_phone(self, phone: str) -> str:
        cleaned = "".join(c for c in phone if c.isdigit() or c == "+")

        if cleaned.startswith("+"):
            return cleaned

        if len(cleaned) == 10 and cleaned[0] in "6789":
            return f"+91{cleaned}"

        if len(cleaned) == 12 and cleaned.startswith("91") and cleaned[2] in "6789":
            return f"+{cleaned}"

        return f"+91{cleaned}"