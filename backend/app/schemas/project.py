from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

class ProjectCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    synopsis: Optional[str] = None
    genre: str = Field(default="Action and adventure")
    language: str = Field(default="English")
    art_style: str = Field(default="Traditional Manga B&W")
    reading_direction: str = Field(default="right-to-left")
    target_audience: str = Field(default="Shonen")
    settings: Optional[Dict[str, Any]] = Field(default_factory=dict)

class ProjectUpdateRequest(BaseModel):
    title: Optional[str] = None
    synopsis: Optional[str] = None
    genre: Optional[str] = None
    language: Optional[str] = None
    art_style: Optional[str] = None
    reading_direction: Optional[str] = None
    target_audience: Optional[str] = None
    status: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None

class ChapterSummaryResponse(BaseModel):
    id: str
    project_id: str
    title: str
    order_index: int
    status: str
    created_at: datetime
    updated_at: datetime

class ProjectResponse(BaseModel):
    id: str
    user_id: str
    title: str
    synopsis: Optional[str] = None
    genre: str
    language: str
    art_style: str
    reading_direction: str
    target_audience: str
    status: str
    settings: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
