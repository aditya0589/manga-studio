import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Integer, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

class Chapter(Base):
    __tablename__ = "chapters"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    story_arc_id = Column(String(36), ForeignKey("story_arcs.id", ondelete="SET NULL"), nullable=True)
    title = Column(String(255), nullable=False)
    synopsis = Column(Text, nullable=True)
    outline = Column(JSON, default=dict, nullable=False) # structured beats, objectives, scene outlines
    status = Column(String(50), default="draft", nullable=False) # draft, outlined, approved, scripted, generated, published
    order_index = Column(Integer, default=1, nullable=False)
    version = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    project = relationship("Project", back_populates="chapters")
    story_arc = relationship("StoryArc", back_populates="chapters")
    scenes = relationship("Scene", back_populates="chapter", cascade="all, delete-orphan", order_by="Scene.order_index")
    pages = relationship("MangaPage", back_populates="chapter", cascade="all, delete-orphan", order_by="MangaPage.page_number")
    exports = relationship("Export", back_populates="chapter", cascade="all, delete-orphan")

class Scene(Base):
    __tablename__ = "scenes"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    chapter_id = Column(String(36), ForeignKey("chapters.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    summary = Column(Text, nullable=True)
    script = Column(JSON, default=dict, nullable=False) # dialogue, actions, characters present, setting
    order_index = Column(Integer, default=1, nullable=False)

    chapter = relationship("Chapter", back_populates="scenes")
    panels = relationship("Panel", back_populates="scene")

class MangaPage(Base):
    __tablename__ = "manga_pages"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    chapter_id = Column(String(36), ForeignKey("chapters.id", ondelete="CASCADE"), nullable=False, index=True)
    page_number = Column(Integer, default=1, nullable=False)
    layout_config = Column(JSON, default=dict, nullable=False) # rows, cols, grid template, border style
    status = Column(String(50), default="draft", nullable=False) # draft, assembled, approved
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    chapter = relationship("Chapter", back_populates="pages")
    panels = relationship("Panel", back_populates="page", cascade="all, delete-orphan", order_by="Panel.panel_number")

class Panel(Base):
    __tablename__ = "panels"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    page_id = Column(String(36), ForeignKey("manga_pages.id", ondelete="CASCADE"), nullable=False, index=True)
    scene_id = Column(String(36), ForeignKey("scenes.id", ondelete="SET NULL"), nullable=True)
    asset_id = Column(String(36), ForeignKey("assets.id", ondelete="SET NULL"), nullable=True)
    panel_number = Column(Integer, default=1, nullable=False)
    script = Column(Text, nullable=True) # Director shot description (camera, composition, character poses)
    image_prompt = Column(Text, nullable=True) # Constructed art generation prompt
    dialogue = Column(JSON, default=list, nullable=False) # [{character_id, speaker_name, text, bubble_type, x, y}]
    narration = Column(JSON, default=list, nullable=False) # [{text, box_type, x, y}]
    sound_effects = Column(JSON, default=list, nullable=False) # [{text, sfx_type, x, y, size}]
    layout_config = Column(JSON, default=dict, nullable=False) # span_cols, span_rows, aspect_ratio
    status = Column(String(50), default="pending", nullable=False) # pending, generating, generated, approved, error
    version = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    page = relationship("MangaPage", back_populates="panels")
    scene = relationship("Scene", back_populates="panels")
    asset = relationship("Asset")
