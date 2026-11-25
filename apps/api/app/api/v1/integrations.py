# Integration API routes

from uuid import UUID

from app.core.dependencies import get_current_organization, get_current_user
from app.db.session import get_db
from app.models.organization import Organization
from app.models.user import User
from app.schemas.integration import (
    IntegrationCreate,
    IntegrationResponse,
    IntegrationUpdate,
)
from app.services.integration_service import IntegrationService
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/integrations", tags=["integrations"])


@router.get("", response_model=list[IntegrationResponse])
async def list_integrations(
    integration_type: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    service = IntegrationService(db)
    return await service.list(organization.id, integration_type)


@router.post("", response_model=IntegrationResponse, status_code=status.HTTP_201_CREATED)
async def create_integration(
    data: IntegrationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    service = IntegrationService(db)
    integration = await service.create(data, organization.id)
    return integration


@router.get("/{integration_id}", response_model=IntegrationResponse)
async def get_integration(
    integration_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    service = IntegrationService(db)
    integration = await service.get_by_id(integration_id, organization.id)
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    return integration


@router.patch("/{integration_id}", response_model=IntegrationResponse)
async def update_integration(
    integration_id: UUID,
    data: IntegrationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    service = IntegrationService(db)
    integration = await service.update(integration_id, organization.id, data)
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    return integration


@router.delete("/{integration_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_integration(
    integration_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    service = IntegrationService(db)
    success = await service.delete(integration_id, organization.id)
    if not success:
        raise HTTPException(status_code=404, detail="Integration not found")


@router.post("/{integration_id}/test", response_model=dict)
async def test_integration(
    integration_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    service = IntegrationService(db)
    return await service.test_integration(integration_id, organization.id)


@router.post("/{integration_id}/sync", response_model=dict)
async def sync_integration(
    integration_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    service = IntegrationService(db)
    return await service.sync_integration(integration_id, organization.id)


@router.get("/google/auth-url")
async def get_google_auth_url(
    type: str = Query(..., pattern="^(sheets|drive)$"),
    campaign_id: UUID | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    """Get Google OAuth authorization URL"""
    from app.core.config import settings
    from google_auth_oauthlib.flow import Flow

    scopes = settings.GOOGLE_SHEETS_SCOPES if type == "sheets" else settings.GOOGLE_DRIVE_SCOPES

    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uris": [settings.GOOGLE_REDIRECT_URI],
            }
        },
        scopes=scopes,
    )
    flow.redirect_uri = settings.GOOGLE_REDIRECT_URI

    state = f"{type}:{campaign_id or ''}:{organization.id}"
    auth_url, _ = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        state=state,
    )

    return {"auth_url": auth_url}


@router.post("/google/callback")
async def handle_google_callback(
    code: str,
    state: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    """Handle Google OAuth callback"""
    # Parse state
    parts = state.split(":")
    integration_type = parts[0]
    campaign_id = UUID(parts[1]) if parts[1] else None


    from app.core.config import settings
    from app.models.enums import IntegrationType
    from app.models.integration import Integration
    from google_auth_oauthlib.flow import Flow

    scopes = settings.GOOGLE_SHEETS_SCOPES if integration_type == "sheets" else settings.GOOGLE_DRIVE_SCOPES

    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uris": [settings.GOOGLE_REDIRECT_URI],
            }
        },
        scopes=scopes,
    )
    flow.redirect_uri = settings.GOOGLE_REDIRECT_URI

    flow.fetch_token(code=code)
    credentials = flow.credentials

    # Create or update integration
    integration_type_enum = IntegrationType.GOOGLE_SHEETS if integration_type == "sheets" else IntegrationType.GOOGLE_DRIVE

    existing = await db.scalar(
        select(Integration).where(
            and_(
                Integration.organization_id == organization.id,
                Integration.type == integration_type_enum,
                Integration.campaign_id == campaign_id,
            )
        )
    )

    config = {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": credentials.scopes,
    }

    if existing:
        existing.config = config
        existing.is_active = True
    else:
        existing = Integration(
            type=integration_type_enum,
            name=f"Google {integration_type.title()}",
            config=config,
            is_active=True,
            organization_id=organization.id,
            campaign_id=campaign_id,
        )
        db.add(existing)

    await db.commit()
    await db.refresh(existing)

    return {"success": True, "integration_id": str(existing.id)}