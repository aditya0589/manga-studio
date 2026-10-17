from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel

class StoryDocumentResponse(BaseModel):
    id: str
    project_id: str
    original_filename: str
    mime_type: str
    storage_key: str
    extracted_text: Optional[str] = None
    processing_status: str
    created_at: datetime

    class Config:
        from_attributes = True

class StoryAnalysisRequest(BaseModel):
    premise_override: Optional[str] = None
    custom_instructions: Optional[str] = None

class StoryBibleGenerateRequest(BaseModel):
    theme: Optional[str] = None
    tone: Optional[str] = None
    world_rules: Optional[List[str]] = None

class StoryBibleResponse(BaseModel):
    premise: str
    synopsis: str
    world_rules: List[str]
    factions_and_locations: List[Dict[str, Any]]
    timeline_events: List[Dict[str, Any]]
    characters: List[Dict[str, Any]]
    plot_arcs: List[Dict[str, Any]]
