# CallRecording model

from typing import Any, Optional
from datetime import datetime
import uuid
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import BaseModel
from app.models.enums import SyncStatus
from sqlalchemy import BigInteger, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


class CallRecording(BaseModel):
    __tablename__ = "call_recordings"

    call_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("calls.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    provider: Mapped[str] = mapped_column(String(50), default="twilio", nullable=False)
    provider_id: Mapped[str] = mapped_column(String(100), nullable=False)
    format: Mapped[str] = mapped_column(String(20), default="mp3", nullable=False)
    duration = Column(Float, nullable=False)  # seconds
    size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    channels: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    sample_rate: Mapped[int] = mapped_column(Integer, default=8000, nullable=False)
    # Google Drive sync
    drive_file_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    drive_synced_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    drive_sync_status: Mapped[SyncStatus] = mapped_column(SQLEnum(SyncStatus), default=SyncStatus.PENDING, nullable=False)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    # Relationships
    call: Mapped[Any] = relationship("Call", back_populates="recording")