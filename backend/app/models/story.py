import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Integer, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

class StoryDocument(Base):
    __tablename__ = "story_documents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    original_filename = Column(String(255), nullable=False)
    mime_type = Column(String(100), nullable=False)
    storage_key = Column(String(500), nullable=False)
    extracted_text = Column(Text, nullable=True)
    processing_status = Column(String(50), default="uploaded", nullable=False) # uploaded, processed, error
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    project = relationship("Project", back_populates="documents")

class StoryArc(Base):
    __tablename__ = "story_arcs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    summary = Column(Text, nullable=True)
    order_index = Column(Integer, default=0, nullable=False)
    outline = Column(JSON, default=dict, nullable=False)

    project = relationship("Project", back_populates="story_arcs")
    chapters = relationship("Chapter", back_populates="story_arc")
