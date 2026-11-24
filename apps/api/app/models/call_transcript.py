# CallTranscript model

from app.models.base import BaseModel
from sqlalchemy import JSON, Column, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


class CallTranscript(BaseModel):
    __tablename__ = "call_transcripts"

    call_id = Column(UUID(as_uuid=True), ForeignKey("calls.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)

    full_text = Column(Text, nullable=False)
    segments = Column(JSON, nullable=False)  # Array of {speaker, text, start_time, end_time, confidence, language}
    language = Column(String(10), default="en-IN", nullable=False)
    word_count = Column(Integer, default=0, nullable=False)
    duration = Column(Integer, nullable=False)  # seconds (stored as integer for precision)

    # Relationships
    call = relationship("Call", back_populates="transcript")