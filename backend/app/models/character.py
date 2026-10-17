import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

class Character(Base):
    __tablename__ = "characters"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    role = Column(String(100), default="Protagonist", nullable=False) # Protagonist, Antagonist, Supporting, Mentor, etc.
    personality = Column(Text, nullable=True)
    appearance = Column(Text, nullable=True)
    canon_data = Column(JSON, default=dict, nullable=False) # hair, eyes, costume, accessories, visual consistency rules
    status = Column(String(50), default="draft", nullable=False) # draft, approved, archived
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    project = relationship("Project", back_populates="characters")
    references = relationship("CharacterReference", back_populates="character", cascade="all, delete-orphan")

class CharacterReference(Base):
    __tablename__ = "character_references"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    character_id = Column(String(36), ForeignKey("characters.id", ondelete="CASCADE"), nullable=False, index=True)
    asset_id = Column(String(36), ForeignKey("assets.id", ondelete="CASCADE"), nullable=False)
    reference_type = Column(String(50), default="canonical_face", nullable=False) # canonical_face, outfit, expression, action_pose
    approval_status = Column(String(50), default="pending", nullable=False) # pending, approved, rejected

    character = relationship("Character", back_populates="references")
    asset = relationship("Asset")
