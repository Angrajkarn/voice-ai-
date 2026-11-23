# Customer service tests

import pytest
from uuid import uuid4
from datetime import datetime

from app.services.customer_service import CustomerService
from app.schemas.customer import CustomerCreate, CustomerUpdate, CustomerImport
from app.models.enums import CustomerStatus, InterestLevel
from app.models.suppression_list import SuppressionList
from app.models.enums import SuppressionReason, SuppressionSource


@pytest.mark.asyncio
async def test_create_customer(db_session, sample_customer_data):
    """Test customer creation"""
    service = CustomerService(db_session)
    org_id = uuid4()

    customer_data = CustomerCreate(**sample_customer_data)
    customer = await service.create(customer_data, org_id)

    assert customer.id is not None
    assert customer.first_name == sample_customer_data["first_name"]
    assert customer.phone == sample_customer_data["phone"]
    assert customer.organization_id == org_id
    assert customer.status == CustomerStatus.NEW


@pytest.mark.asyncio
async def test_create_duplicate_customer(db_session, sample_customer_data):
    """Test duplicate customer prevention"""
    service = CustomerService(db_session)
    org_id = uuid4()

    customer_data = CustomerCreate(**sample_customer_data)
    await service.create(customer_data, org_id)

    # Try to create duplicate
    with pytest.raises(ValueError, match="already exists"):
        await service.create(customer_data, org_id)


@pytest.mark.asyncio
async def test_create_customer_suppressed(db_session, sample_customer_data):
    """Test customer creation with suppression list"""
    service = CustomerService(db_session)
    org_id = uuid4()

    # Add to suppression list
    suppression = SuppressionList(
        phone=sample_customer_data["phone"],
        reason=SuppressionReason.OPT_OUT,
        source=SuppressionSource.MANUAL,
        organization_id=org_id,
        is_active=True,
    )
    db_session.add(suppression)
    await db_session.commit()

    customer_data = CustomerCreate(**sample_customer_data)
    with pytest.raises(ValueError, match="suppression list"):
        await service.create(customer_data, org_id)


@pytest.mark.asyncio
async def test_get_customer(db_session, sample_customer_data):
    """Test getting customer by ID"""
    service = CustomerService(db_session)
    org_id = uuid4()

    customer_data = CustomerCreate(**sample_customer_data)
    created = await service.create(customer_data, org_id)

    retrieved = await service.get_by_id(created.id, org_id)
    assert retrieved is not None
    assert retrieved.id == created.id


@pytest.mark.asyncio
async def test_list_customers(db_session, sample_customer_data):
    """Test listing customers with filters"""
    service = CustomerService(db_session)
    org_id = uuid4()

    # Create multiple customers
    for i in range(10):
        data = CustomerCreate(**{
            **sample_customer_data,
            "first_name": f"Customer{i}",
            "phone": f"+1555123456{i}",
            "email": f"customer{i}@example.com",
        })
        await service.create(data, org_id)

    # List with pagination
    customers, total = await service.list(organization_id=org_id, page=1, page_size=5)
    assert total == 10
    assert len(customers) == 5

    # List with status filter
    customers, total = await service.list(organization_id=org_id, status=CustomerStatus.NEW)
    assert total == 10


@pytest.mark.asyncio
async def test_update_customer(db_session, sample_customer_data):
    """Test customer update"""
    service = CustomerService(db_session)
    org_id = uuid4()

    customer_data = CustomerCreate(**sample_customer_data)
    created = await service.create(customer_data, org_id)

    update_data = CustomerUpdate(
        company="Updated Corp",
        interest_level=InterestLevel.HOT,
        status=CustomerStatus.HOT_LEAD,
    )
    updated = await service.update(created.id, org_id, update_data)

    assert updated is not None
    assert updated.company == "Updated Corp"
    assert updated.interest_level == InterestLevel.HOT
    assert updated.status == CustomerStatus.HOT_LEAD


@pytest.mark.asyncio
async def test_bulk_import_customers(db_session, sample_customer_data):
    """Test bulk customer import"""
    service = CustomerService(db_session)
    org_id = uuid4()

    import_data = CustomerImport(
        customers=[
            CustomerCreate(**{
                **sample_customer_data,
                "first_name": f"Import{i}",
                "phone": f"+1555123456{i}",
                "email": f"import{i}@example.com",
            })
            for i in range(5)
        ],
        skip_duplicates=True,
    )

    result = await service.bulk_import(import_data, org_id)
    assert result["successful"] == 5
    assert result["failed"] == 0
    assert result["duplicates"] == 0


@pytest.mark.asyncio
async def test_bulk_import_with_duplicates(db_session, sample_customer_data):
    """Test bulk import with duplicate handling"""
    service = CustomerService(db_session)
    org_id = uuid4()

    # Create existing customer
    existing_data = CustomerCreate(**sample_customer_data)
    await service.create(existing_data, org_id)

    import_data = CustomerImport(
        customers=[
            CustomerCreate(**{
                **sample_customer_data,
                "first_name": "Import1",
                "phone": "+15551234567",  # Same as existing
            }),
            CustomerCreate(**{
                **sample_customer_data,
                "first_name": "Import2",
                "phone": "+15551234568",
            }),
        ],
        skip_duplicates=True,
    )

    result = await service.bulk_import(import_data, org_id)
    assert result["successful"] == 1  # Only the new one
    assert result["duplicates"] == 1


@pytest.mark.asyncio
async def test_mark_do_not_call(db_session, sample_customer_data):
    """Test marking customers as do not call"""
    service = CustomerService(db_session)
    org_id = uuid4()

    # Create customers
    customer_ids = []
    for i in range(3):
        data = CustomerCreate(**{
            **sample_customer_data,
            "first_name": f"DoNotCall{i}",
            "phone": f"+1555123456{i}",
            "email": f"dnc{i}@example.com",
        })
        customer = await service.create(data, org_id)
        customer_ids.append(customer.id)

    # Mark as do not call
    updated = await service.mark_do_not_call(customer_ids, org_id)
    assert updated == 3

    # Verify suppression list entries
    from sqlalchemy import select
    suppressions = await db_session.execute(
        select(SuppressionList).where(SuppressionList.organization_id == org_id)
    )
    assert len(suppressions.scalars().all()) == 3


@pytest.mark.asyncio
async def test_schedule_callback(db_session, sample_customer_data):
    """Test scheduling callbacks"""
    service = CustomerService(db_session)
    org_id = uuid4()

    # Create customer
    customer_data = CustomerCreate(**sample_customer_data)
    customer = await service.create(customer_data, org_id)

    callback_date = datetime(2025, 1, 15, 10, 0, 0)
    scheduled = await service.schedule_callback(
        [customer.id], org_id, callback_date
    )
    assert scheduled == 1

    # Verify callback created
    from app.models.callback import Callback
    from app.models.enums import CallbackStatus
    callbacks = await db_session.execute(
        select(Callback).where(
            Callback.customer_id == customer.id,
            Callback.status == CallbackStatus.SCHEDULED,
        )
    )
    callback = callbacks.scalar_one_or_none()
    assert callback is not None
    assert callback.scheduled_at == callback_date