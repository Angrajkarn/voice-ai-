# CallTranscript model

from typing import Any
import uuid
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import BaseModel
from sqlalchemy import ForeignKey, Float, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship


class CallTranscript(BaseModel):
    __tablename__ = "call_transcripts"

    call_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("calls.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    full_text: Mapped[str] = mapped_column(Text, nullable=False)
    segments: Mapped[Any] = mapped_column(JSONB, nullable=False)  # Array of {speaker, text, start_time, end_time, confidence, language}
    language: Mapped[str] = mapped_column(String(10), default="en-IN", nullable=False)
    word_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    duration: Mapped[float] = mapped_column(Float, nullable=False)  # seconds

    # Relationships
    call: Mapped[Any] = relationship("Call", back_populates="transcript")