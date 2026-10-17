from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

class CharacterCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    role: str = Field(default="Protagonist")
    personality: Optional[str] = None
    appearance: Optional[str] = None
    canon_data: Optional[Dict[str, Any]] = Field(default_factory=dict)

class CharacterUpdateRequest(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    personality: Optional[str] = None
    appearance: Optional[str] = None
    canon_data: Optional[Dict[str, Any]] = None
    status: Optional[str] = None

class ReferenceResponse(BaseModel):
    id: str
    character_id: str
    asset_id: str
    reference_type: str
    approval_status: str
    image_url: Optional[str] = None

    class Config:
        from_attributes = True

class CharacterResponse(BaseModel):
    id: str
    project_id: str
    name: str
    role: str
    personality: Optional[str] = None
    appearance: Optional[str] = None
    canon_data: Dict[str, Any]
    status: str
    created_at: datetime
    updated_at: datetime
    references: List[ReferenceResponse] = []

    class Config:
        from_attributes = True

class ApproveDesignRequest(BaseModel):
    reference_id: Optional[str] = None
    canonical_appearance: Optional[str] = None
    visual_consistency_rules: Optional[List[str]] = None
