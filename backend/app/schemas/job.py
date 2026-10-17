from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel

class JobResponse(BaseModel):
    id: str
    project_id: str
    chapter_id: Optional[str] = None
    job_type: str
    status: str
    progress: int
    current_stage: str
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    usage_metadata: Dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class JobEventPayload(BaseModel):
    event: str
    data: Dict[str, Any]
