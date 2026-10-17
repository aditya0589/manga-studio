from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

class ChapterCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    synopsis: Optional[str] = None
    order_index: Optional[int] = 1

class ChapterUpdateRequest(BaseModel):
    title: Optional[str] = None
    synopsis: Optional[str] = None
    outline: Optional[Dict[str, Any]] = None
    status: Optional[str] = None

class ChapterApproveRequest(BaseModel):
    approved_beats: Optional[List[str]] = None
    comments: Optional[str] = None

class ChapterReviseRequest(BaseModel):
    revision_feedback: str
    target_sections: Optional[List[str]] = None

class SceneResponse(BaseModel):
    id: str
    chapter_id: str
    title: str
    summary: Optional[str]
    script: Dict[str, Any]
    order_index: int

    class Config:
        from_attributes = True

class DialogueItem(BaseModel):
    character_id: Optional[str] = None
    speaker_name: str
    text: str
    bubble_type: str = "speech" # speech, thought, shout, whisper
    x: Optional[float] = 15.0 # percentage or coordinates on panel
    y: Optional[float] = 15.0

class NarrationItem(BaseModel):
    text: str
    box_type: str = "caption" # caption, time_jump, location
    x: Optional[float] = 5.0
    y: Optional[float] = 5.0

class SoundEffectItem(BaseModel):
    text: str
    sfx_type: str = "dramatic" # dramatic, impact, motion, ambient
    x: Optional[float] = 50.0
    y: Optional[float] = 50.0
    size: Optional[str] = "medium"

class PanelUpdateRequest(BaseModel):
    script: Optional[str] = None
    image_prompt: Optional[str] = None
    dialogue: Optional[List[Dict[str, Any]]] = None
    narration: Optional[List[Dict[str, Any]]] = None
    sound_effects: Optional[List[Dict[str, Any]]] = None
    layout_config: Optional[Dict[str, Any]] = None
    status: Optional[str] = None
    panel_number: Optional[int] = None

class PanelGenerateRequest(BaseModel):
    custom_prompt: Optional[str] = None
    character_ids: Optional[List[str]] = None
    apply_style: bool = True

class PanelResponse(BaseModel):
    id: str
    page_id: str
    scene_id: Optional[str] = None
    asset_id: Optional[str] = None
    image_url: Optional[str] = None
    panel_number: int
    script: Optional[str]
    image_prompt: Optional[str]
    dialogue: List[Dict[str, Any]] = []
    narration: List[Dict[str, Any]] = []
    sound_effects: List[Dict[str, Any]] = []
    layout_config: Dict[str, Any] = {}
    status: str
    version: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class PageResponse(BaseModel):
    id: str
    chapter_id: str
    page_number: int
    layout_config: Dict[str, Any] = {}
    status: str
    created_at: datetime
    panels: List[PanelResponse] = []

    class Config:
        from_attributes = True

class ChapterResponse(BaseModel):
    id: str
    project_id: str
    story_arc_id: Optional[str] = None
    title: str
    synopsis: Optional[str]
    outline: Dict[str, Any]
    status: str
    order_index: int
    version: int
    created_at: datetime
    updated_at: datetime
    scenes: List[SceneResponse] = []
    pages: List[PageResponse] = []

    class Config:
        from_attributes = True
