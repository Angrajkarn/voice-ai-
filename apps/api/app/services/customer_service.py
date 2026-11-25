# Customer Service

import builtins
import csv
import io
from datetime import datetime
from typing import Any
from uuid import UUID

from app.models.campaign_customer import CampaignCustomer
from app.models.customer import Customer
from app.models.enums import CustomerStatus, SuppressionReason, SuppressionSource
from app.models.suppression_list import SuppressionList
from app.schemas.customer import CustomerCreate, CustomerImport, CustomerUpdate
from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession


class CustomerService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: CustomerCreate, organization_id: UUID) -> Customer:
        # Normalize phone number
        phone = self._normalize_phone(data.phone)

        # Check for duplicate
        existing = await self.db.scalar(
            select(Customer).where(
                and_(
                    Customer.organization_id == organization_id,
                    Customer.phone == phone,
                )
            )
        )
        if existing:
            raise ValueError(f"Customer with phone {phone} already exists")

        # Check suppression list
        suppressed = await self.db.scalar(
            select(SuppressionList).where(
                and_(
                    SuppressionList.organization_id == organization_id,
                    SuppressionList.phone == phone,
                    SuppressionList.is_active.is_(True),
                )
            )
        )
        if suppressed:
            raise ValueError(f"Phone number {phone} is on suppression list")

        customer_values = data.model_dump()
        customer_values["phone"] = phone
        customer = Customer(
            **customer_values,
            organization_id=organization_id,
        )
        self.db.add(customer)
        await self.db.commit()
        await self.db.refresh(customer)
        return customer

    async def bulk_import(
        self,
        data: CustomerImport,
        organization_id: UUID,
    ) -> dict[str, Any]:
        successful = 0
        failed = 0
        duplicates = 0
        errors = []

        for idx, customer_data in enumerate(data.customers):
            try:
                phone = self._normalize_phone(customer_data.phone)

                # Check duplicate
                existing = await self.db.scalar(
                    select(Customer).where(
                        and_(
                            Customer.organization_id == organization_id,
                            Customer.phone == phone,
                        )
                    )
                )

                if existing:
                    if data.update_existing:
                        # Update existing
                        update_data = customer_data.model_dump(exclude_unset=True)
                        update_data["phone"] = phone
                        for key, value in update_data.items():
                            setattr(existing, key, value)
                        await self.db.commit()
                        successful += 1
                    else:
                        duplicates += 1
                        if not data.skip_duplicates:
                            failed += 1
                            errors.append({
                                "row": idx + 1,
                                "field": "phone",
                                "value": phone,
                                "error": "Duplicate phone number",
                            })
                    continue

                # Check suppression
                suppressed = await self.db.scalar(
                    select(SuppressionList).where(
                        and_(
                            SuppressionList.organization_id == organization_id,
                            SuppressionList.phone == phone,
                            SuppressionList.is_active.is_(True),
                        )
                    )
                )
                if suppressed:
                    failed += 1
                    errors.append({
                        "row": idx + 1,
                        "field": "phone",
                        "value": phone,
                        "error": "Phone number on suppression list",
                    })
                    continue

                # Create customer
                customer_values = customer_data.model_dump()
                customer_values["phone"] = phone
                customer = Customer(
                    **customer_values,
                    organization_id=organization_id,
                )
                self.db.add(customer)
                successful += 1

            except Exception as e:
                failed += 1
                errors.append({
                    "row": idx + 1,
                    "field": "unknown",
                    "value": str(customer_data),
                    "error": str(e),
                })

        await self.db.commit()

        return {
            "successful": successful,
            "failed": failed,
            "duplicates": duplicates,
            "errors": errors,
        }

    async def import_from_csv(
        self,
        file_content: bytes,
        organization_id: UUID,
        campaign_id: UUID | None = None,
        skip_duplicates: bool = True,
        update_existing: bool = False,
    ) -> dict[str, Any]:
        # Parse CSV
        text = file_content.decode("utf-8")
        reader = csv.DictReader(io.StringIO(text))

        customers_data = []
        for row in reader:
            # Map CSV columns to customer fields
            customer = self._map_csv_row(row)
            if customer:
                customers_data.append(customer)

        import_data = CustomerImport(
            customers=[CustomerCreate(**c) for c in customers_data],
            skip_duplicates=skip_duplicates,
            update_existing=update_existing,
        )

        result = await self.bulk_import(import_data, organization_id)

        # If campaign_id provided, add customers to campaign
        if campaign_id and result["successful"] > 0:
            # Get newly created customers
            new_customers = await self.db.execute(
                select(Customer).where(
                    and_(
                        Customer.organization_id == organization_id,
                        Customer.phone.in_([c["phone"] for c in customers_data]),
                    )
                )
            )
            customers = new_customers.scalars().all()

            # Add to campaign
            for customer in customers:
                existing_link = await self.db.scalar(
                    select(CampaignCustomer).where(
                        and_(
                            CampaignCustomer.campaign_id == campaign_id,
                            CampaignCustomer.customer_id == created_customer.id,
                        )
                    )
                )
                if not existing_link:
                    link = CampaignCustomer(
                        campaign_id=campaign_id,
                        customer_id=created_customer.id,
                        status=CustomerStatus.NEW,
                    )
                    self.db.add(link)

            await self.db.commit()

        return result

    def _map_csv_row(self, row: dict[str, str]) -> dict[str, Any] | None:
        # Default column mapping
        column_map = {
            "first_name": "first_name",
            "firstname": "first_name",
            "first name": "first_name",
            "last_name": "last_name",
            "lastname": "last_name",
            "last name": "last_name",
            "email": "email",
            "phone": "phone",
            "phone_number": "phone",
            "phone number": "phone",
            "mobile": "phone",
            "company": "company",
            "location": "location",
            "city": "location",
            "language": "language",
            "timezone": "timezone",
            "tags": "tags",
        }

        customer = {}
        for csv_col, field in column_map.items():
            # Find matching column (case-insensitive)
            matched_key = next(
                (k for k in row if k.lower().strip() == csv_col.lower()),
                None
            )
            if matched_key and row[matched_key]:
                value: str | list[str] = row[matched_key].strip()
                if field == "phone":
                    value = self._normalize_phone(value)
                elif field == "tags":
                    value = [t.strip() for t in value.split(",") if t.strip()]
                customer[field] = value

        # Validate required fields
        if not customer.get("first_name") or not customer.get("phone"):
            return None

        return customer

    def _normalize_phone(self, phone: str) -> str:
        # Remove all non-digits except +
        cleaned = "".join(c for c in phone if c.isdigit() or c == "+")

        # Already in E.164 format
        if cleaned.startswith("+"):
            return cleaned

        # Indian mobile number (10 digits starting with 6-9)
        if len(cleaned) == 10 and cleaned[0] in "6789":
            return f"+91{cleaned}"

        # Indian number with country code (12 digits starting with 91)
        if len(cleaned) == 12 and cleaned.startswith("91") and cleaned[2] in "6789":
            return f"+{cleaned}"

        # Default: assume Indian number
        return f"+91{cleaned}"

    async def get_by_id(self, customer_id: UUID, organization_id: UUID) -> Customer | None:
        result = await self.db.execute(
            select(Customer).where(
                and_(
                    Customer.id == customer_id,
                    Customer.organization_id == organization_id,
                )
            )
        )
        return result.scalar_one_or_none()

    async def list(
        self,
        organization_id: UUID,
        page: int = 1,
        page_size: int = 20,
        campaign_id: UUID | None = None,
        status: str | None = None,
        interest_level: str | None = None,
        language: str | None = None,
        search: str | None = None,
        has_callback: bool | None = None,
        do_not_call: bool | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> tuple[list[Customer], int]:
        query = select(Customer).where(Customer.organization_id == organization_id)

        if campaign_id:
            query = query.join(CampaignCustomer).where(CampaignCustomer.campaign_id == campaign_id)

        if status:
            query = query.where(Customer.status == status)

        if interest_level:
            query = query.where(Customer.interest_level == interest_level)

        if language:
            query = query.where(Customer.language == language)

        if has_callback:
            query = query.where(Customer.next_callback_at.isnot(None))

        if do_not_call is not None:
            query = query.where(Customer.do_not_call == do_not_call)

        if search:
            query = query.where(
                or_(
                    Customer.first_name.ilike(f"%{search}%"),
                    Customer.last_name.ilike(f"%{search}%"),
                    Customer.phone.ilike(f"%{search}%"),
                    Customer.email.ilike(f"%{search}%"),
                    Customer.company.ilike(f"%{search}%"),
                )
            )

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total = await self.db.scalar(count_query) or 0

        # Apply sorting
        sort_column = getattr(Customer, sort_by, Customer.created_at)
        if sort_order == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())

        # Apply pagination
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await self.db.execute(query)
        customers = result.scalars().all()

        return list(customers), total

    async def update(self, customer_id: UUID, organization_id: UUID, data: CustomerUpdate) -> Customer | None:
        customer = await self.get_by_id(customer_id, organization_id)
        if not customer:
            return None

        update_data = data.model_dump(exclude_unset=True)
        if "phone" in update_data:
            update_data["phone"] = self._normalize_phone(update_data["phone"])

        for key, value in update_data.items():
            setattr(customer, key, value)

        await self.db.commit()
        await self.db.refresh(customer)
        return customer

    async def delete(self, customer_id: UUID, organization_id: UUID) -> bool:
        customer = await self.get_by_id(customer_id, organization_id)
        if not customer:
            return False

        await self.db.delete(customer)
        await self.db.commit()
        return True

    async def add_to_campaign(
        self,
        campaign_id: UUID,
        customer_ids: builtins.list[UUID],
        organization_id: UUID,
    ) -> dict[str, Any]:
        added = 0
        skipped = 0

        for customer_id in customer_ids:
            customer = await self.get_by_id(customer_id, organization_id)
            if not customer:
                skipped += 1
                continue

            existing = await self.db.scalar(
                select(CampaignCustomer).where(
                    and_(
                        CampaignCustomer.campaign_id == campaign_id,
                        CampaignCustomer.customer_id == customer_id,
                    )
                )
            )
            if existing:
                skipped += 1
                continue

            link = CampaignCustomer(
                campaign_id=campaign_id,
                customer_id=customer_id,
                status=CustomerStatus.NEW,
            )
            self.db.add(link)
            added += 1

        await self.db.commit()
        return {"added": added, "skipped": skipped}

    async def remove_from_campaign(
        self,
        campaign_id: UUID,
        customer_ids: builtins.list[UUID],
    ) -> int:
        result = await self.db.execute(
            select(CampaignCustomer).where(
                and_(
                    CampaignCustomer.campaign_id == campaign_id,
                    CampaignCustomer.customer_id.in_(customer_ids),
                )
            )
        )
        links = result.scalars().all()

        for link in links:
            await self.db.delete(link)

        await self.db.commit()
        return len(links)

    async def mark_do_not_call(
        self,
        customer_ids: builtins.list[UUID],
        organization_id: UUID,
        reason: str = "MANUAL",
    ) -> int:
        updated = 0
        for customer_id in customer_ids:
            customer = await self.get_by_id(customer_id, organization_id)
            if customer:
                customer.do_not_call = True
                customer.status = CustomerStatus.DO_NOT_CALL

                # Add to suppression list
                suppression = SuppressionList(
                    phone=customer.phone,
                    reason=SuppressionReason.OPT_OUT,
                    source=SuppressionSource.MANUAL,
                    organization_id=organization_id,
                    customer_id=customer_id,
                    is_active=True,
                )
                self.db.add(suppression)
                updated += 1

        await self.db.commit()
        return updated

    async def schedule_callback(
        self,
        customer_ids: builtins.list[UUID],
        organization_id: UUID,
        callback_date: datetime,
        campaign_id: UUID | None = None,
    ) -> int:
        scheduled = 0
        for customer_id in customer_ids:
            customer = await self.get_by_id(customer_id, organization_id)
            if not customer:
                continue

            customer.next_callback_at = callback_date
            customer.status = CustomerStatus.CALLBACK_REQUESTED

            # Create callback record
            from app.models.callback import Callback
            from app.models.enums import CallbackStatus
            selected_campaign_id = campaign_id or await self.db.scalar(
                select(CampaignCustomer.campaign_id)
                .where(CampaignCustomer.customer_id == customer_id)
                .order_by(CampaignCustomer.assigned_at.desc())
                .limit(1)
            )
            if selected_campaign_id is None:
                continue

            callback = Callback(
                status=CallbackStatus.SCHEDULED,
                scheduled_at=callback_date,
                scheduled_timezone=customer.timezone,
                campaign_id=selected_campaign_id,
                customer_id=customer_id,
            )
            self.db.add(callback)
            scheduled += 1

        await self.db.commit()
        return scheduled

    async def export_customers(
        self,
        organization_id: UUID,
        campaign_id: UUID | None = None,
        format: str = "csv",
    ) -> bytes:
        customers, _ = await self.list(organization_id, page=1, page_size=10000, campaign_id=campaign_id)

        if format == "csv":
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow([
                "id", "first_name", "last_name", "email", "phone", "phone_raw",
                "company", "location", "language", "timezone", "tags",
                "status", "interest_level", "call_attempts", "last_call_at",
                "next_callback_at", "do_not_call", "created_at"
            ])
            for c in customers:
                writer.writerow([
                    c.id, c.first_name, c.last_name, c.email, c.phone, c.phone_raw,
                    c.company, c.location, c.language, c.timezone, ",".join(c.tags),
                    c.status.value, c.interest_level.value, c.call_attempts,
                    c.last_call_at.isoformat() if c.last_call_at else "",
                    c.next_callback_at.isoformat() if c.next_callback_at else "",
                    c.do_not_call,
                    c.created_at.isoformat()
                ])
            return output.getvalue().encode("utf-8")

        # For xlsx, would use openpyxl
        return b""