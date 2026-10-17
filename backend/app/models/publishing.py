import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Float, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

class Export(Base):
    __tablename__ = "exports"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    chapter_id = Column(String(36), ForeignKey("chapters.id", ondelete="CASCADE"), nullable=False, index=True)
    format = Column(String(20), default="pdf", nullable=False) # pdf, cbz
    storage_key = Column(String(500), nullable=False)
    status = Column(String(50), default="processing", nullable=False) # processing, completed, failed
    settings = Column(JSON, default=dict, nullable=False) # page_size, reading_direction, print_mode, dpi
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    project = relationship("Project", back_populates="exports")
    chapter = relationship("Chapter", back_populates="exports")

class UsageRecord(Base):
    __tablename__ = "usage_records"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="SET NULL"), nullable=True, index=True)
    provider = Column(String(50), nullable=False) # openrouter, cloudflare, mock
    model = Column(String(100), nullable=False)
    operation = Column(String(50), nullable=False) # text_generation, image_generation
    request_count = Column(Integer, default=1, nullable=False)
    estimated_cost = Column(Float, default=0.0, nullable=False)
    status = Column(String(50), default="success", nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    user = relationship("User", back_populates="usage_records")
    project = relationship("Project", back_populates="usage_records")
