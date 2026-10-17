import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

class Project(Base):
    __tablename__ = "projects"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    synopsis = Column(Text, nullable=True)
    genre = Column(String(100), default="Action and adventure", nullable=False)
    language = Column(String(50), default="English", nullable=False)
    art_style = Column(String(100), default="Traditional Manga B&W", nullable=False)
    reading_direction = Column(String(20), default="right-to-left", nullable=False) # 'right-to-left' (manga) or 'left-to-right'
    target_audience = Column(String(100), default="Shonen", nullable=False)
    status = Column(String(50), default="draft", nullable=False) # draft, planning, generated, published, archived
    settings = Column(JSON, default=dict, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    user = relationship("User", back_populates="projects")
    documents = relationship("StoryDocument", back_populates="project", cascade="all, delete-orphan")
    characters = relationship("Character", back_populates="project", cascade="all, delete-orphan")
    story_arcs = relationship("StoryArc", back_populates="project", cascade="all, delete-orphan")
    chapters = relationship("Chapter", back_populates="project", cascade="all, delete-orphan")
    assets = relationship("Asset", back_populates="project", cascade="all, delete-orphan")
    jobs = relationship("GenerationJob", back_populates="project", cascade="all, delete-orphan")
    exports = relationship("Export", back_populates="project", cascade="all, delete-orphan")
    usage_records = relationship("UsageRecord", back_populates="project", cascade="all, delete-orphan")
