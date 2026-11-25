# Customer API routes

from typing import Any
from uuid import UUID

from app.core.dependencies import get_current_organization, get_current_user
from app.db.session import get_db
from app.models.organization import Organization
from app.models.user import User
from app.schemas.customer import (
    CustomerBulkAction,
    CustomerCreate,
    CustomerImport,
    CustomerResponse,
    CustomerUpdate,
)
from app.services.customer_service import CustomerService
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/customers", tags=["customers"])


@router.get("", response_model=dict)
async def list_customers(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    campaign_id: UUID | None = None,
    status: str | None = None,
    interest_level: str | None = None,
    language: str | None = None,
    search: str | None = None,
    has_callback: bool | None = None,
    do_not_call: bool | None = None,
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    service = CustomerService(db)
    customers, total = await service.list(
        organization_id=organization.id,
        page=page,
        page_size=page_size,
        campaign_id=campaign_id,
        status=status,
        interest_level=interest_level,
        language=language,
        search=search,
        has_callback=has_callback,
        do_not_call=do_not_call,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    return {
        "data": customers,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
    }


@router.post("", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
async def create_customer(
    data: CustomerCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    service = CustomerService(db)
    try:
        customer = await service.create(data, organization.id)
        return customer
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/import", response_model=dict)
async def import_customers(
    data: CustomerImport,
    campaign_id: UUID | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    service = CustomerService(db)
    result = await service.bulk_import(data, organization.id)
    return result


@router.post("/import/csv", response_model=dict)
async def import_customers_csv(
    file: UploadFile = File(...),
    campaign_id: UUID | None = None,
    skip_duplicates: bool = True,
    update_existing: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    service = CustomerService(db)
    content = await file.read()
    result = await service.import_from_csv(
        content,
        organization.id,
        campaign_id,
        skip_duplicates,
        update_existing,
    )
    return result


@router.get("/export")
async def export_customers(
    campaign_id: UUID | None = None,
    format: str = Query("csv", pattern="^(csv|xlsx)$"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    service = CustomerService(db)
    content = await service.export_customers(organization.id, campaign_id, format)

    from fastapi.responses import Response
    media_type = "text/csv" if format == "csv" else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    filename = f"customers_export.{format}"

    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(
    customer_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    service = CustomerService(db)
    customer = await service.get_by_id(customer_id, organization.id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@router.patch("/{customer_id}", response_model=CustomerResponse)
async def update_customer(
    customer_id: UUID,
    data: CustomerUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    service = CustomerService(db)
    customer = await service.update(customer_id, organization.id, data)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_customer(
    customer_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    service = CustomerService(db)
    success = await service.delete(customer_id, organization.id)
    if not success:
        raise HTTPException(status_code=404, detail="Customer not found")


@router.post("/bulk", response_model=dict)
async def bulk_customer_action(
    data: CustomerBulkAction,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    service = CustomerService(db)
    results: dict[str, Any] = {"success": 0, "failed": 0, "errors": []}

    for customer_id in data.customer_ids:
        try:
            if data.action == "add_to_campaign":
                if not data.campaign_id:
                    raise ValueError("campaign_id required for add_to_campaign")
                await service.add_to_campaign(data.campaign_id, [customer_id], organization.id)
            elif data.action == "remove_from_campaign":
                if not data.campaign_id:
                    raise ValueError("campaign_id required for remove_from_campaign")
                await service.remove_from_campaign(data.campaign_id, [customer_id])
            elif data.action == "mark_do_not_call":
                await service.mark_do_not_call([customer_id], organization.id)
            elif data.action == "schedule_callback":
                if not data.callback_date:
                    raise ValueError("callback_date required for schedule_callback")
                await service.schedule_callback([customer_id], organization.id, data.callback_date, data.campaign_id)
            elif data.action == "delete":
                await service.delete(customer_id, organization.id)
            results["success"] += 1
        except Exception as e:
            results["failed"] += 1
            results["errors"].append({"customer_id": str(customer_id), "error": str(e)})

    return results