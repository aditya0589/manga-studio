import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Integer, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

class GenerationJob(Base):
    __tablename__ = "generation_jobs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    chapter_id = Column(String(36), ForeignKey("chapters.id", ondelete="SET NULL"), nullable=True, index=True)
    job_type = Column(String(50), nullable=False) # story_analyze, story_bible, chapter_plan, panel_generation, chapter_full, export_pdf
    status = Column(String(50), default="queued", nullable=False) # queued, running, approval_required, completed, failed, cancelled
    progress = Column(Integer, default=0, nullable=False) # 0 to 100
    current_stage = Column(String(100), default="initialized", nullable=False)
    error_code = Column(String(50), nullable=True)
    error_message = Column(Text, nullable=True)
    usage_metadata = Column(JSON, default=dict, nullable=False)
    retry_count = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    project = relationship("Project", back_populates="jobs")
    chapter = relationship("Chapter")

class WorkflowMetadata(Base):
    __tablename__ = "workflow_metadata"

    workflow_id = Column(String(100), primary_key=True)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    current_stage = Column(String(100), nullable=False)
    checkpoint_reference = Column(JSON, default=dict, nullable=False)
    status = Column(String(50), default="active", nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
