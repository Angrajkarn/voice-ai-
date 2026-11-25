"""Firebase-backed account bootstrap and application JWT exchange."""
import re
from datetime import datetime, timezone

import firebase_admin
from firebase_admin import auth as firebase_auth, credentials
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.dependencies import (
    create_access_token,
    create_refresh_token,
    get_current_organization,
    get_current_user,
)
from app.db.session import get_db
from app.models.enums import OrganizationPlan, UserRole
from app.models.organization import Organization
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


def _firebase_app():
    try:
        return firebase_admin.get_app()
    except ValueError:
        if not settings.FIREBASE_PROJECT_ID:
            raise HTTPException(status_code=503, detail="Firebase authentication is not configured")
        options = {"projectId": settings.FIREBASE_PROJECT_ID}
        if settings.FIREBASE_SERVICE_ACCOUNT_JSON:
            import json
            credential = credentials.Certificate(json.loads(settings.FIREBASE_SERVICE_ACCOUNT_JSON))
            return firebase_admin.initialize_app(credential, options)
        return firebase_admin.initialize_app(options=options)


class FirebaseSessionRequest(BaseModel):
    id_token: str = Field(min_length=20)
    workspace_name: str | None = Field(default=None, max_length=100)


@router.post("/firebase/session")
async def firebase_session(payload: FirebaseSessionRequest, db: AsyncSession = Depends(get_db)):
    """Verify Firebase ID token, provision the first workspace, and issue app JWTs."""
    try:
        decoded = firebase_auth.verify_id_token(payload.id_token, app=_firebase_app(), check_revoked=True)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired Firebase session")
    email = decoded.get("email")
    if not email or not decoded.get("email_verified", False):
        raise HTTPException(status_code=403, detail="Verify your email address before continuing")
    email = email.strip().lower()
    user = await db.scalar(select(User).where(User.email == email))
    if user is None:
        workspace = (payload.workspace_name or (email.split("@")[0] + "'s workspace")).strip()
        base_slug = re.sub(r"[^a-z0-9]+", "-", workspace.lower()).strip("-")[:40] or "workspace"
        slug = base_slug
        suffix = 1
        while await db.scalar(select(Organization.id).where(Organization.slug == slug)):
            suffix += 1
            slug = f"{base_slug[:35]}-{suffix}"
        organization = Organization(name=workspace, slug=slug, plan=OrganizationPlan.FREE)
        db.add(organization)
        await db.flush()
        user = User(
            email=email,
            name=decoded.get("name") or email.split("@")[0],
            avatar_url=decoded.get("picture"),
            role=UserRole.ADMIN,
            organization_id=organization.id,
            is_active=True,
        )
        db.add(user)
        await db.flush()
    if not user.is_active:
        raise HTTPException(status_code=403, detail="This account is disabled")
    user.last_login_at = datetime.now(timezone.utc)
    claims = {"sub": str(user.id), "organization_id": str(user.organization_id), "role": user.role.value}
    return {
        "access_token": create_access_token(claims),
        "refresh_token": create_refresh_token(claims),
        "token_type": "bearer",
        "user": {
            "id": str(user.id),
            "email": user.email,
            "name": user.name,
            "avatar_url": user.avatar_url,
            "organization_id": str(user.organization_id),
            "role": user.role.value,
        },
    }


@router.get("/me")
async def get_my_profile(
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    """Return the signed-in user's real profile and workspace."""
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "name": current_user.name,
        "avatar_url": current_user.avatar_url,
        "role": current_user.role.value,
        "organization_id": str(organization.id),
        "organization_name": organization.name,
    }
