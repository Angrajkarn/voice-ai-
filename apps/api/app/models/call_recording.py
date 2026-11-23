# CallRecording model

from sqlalchemy import Column, String, DateTime, ForeignKey, Text, JSON, Integer, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
from app.models.enums import SyncStatus
import uuid


class CallRecording(BaseModel):
    __tablename__ = "call_recordings"

    call_id = Column(UUID(as_uuid=True), ForeignKey("calls.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)

    url = Column(String(500), nullable=False)
    provider = Column(String(50), default="twilio", nullable=False)
    provider_id = Column(String(100), nullable=False)
    format = Column(String(20), default="mp3", nullable=False)
    duration = Column(Integer, nullable=False)  # seconds
    size_bytes = Column(Integer, nullable=False)
    channels = Column(Integer, default=1, nullable=False)
    sample_rate = Column(Integer, default=8000, nullable=False)

    # Google Drive sync
    drive_file_id = Column(String(100), nullable=True)
    drive_synced_at = Column(DateTime(timezone=True), nullable=True)
    drive_sync_status = Column(SQLEnum(SyncStatus), default=SyncStatus.PENDING, nullable=False)

    expires_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    call = relationship("Call", back_populates="recording")