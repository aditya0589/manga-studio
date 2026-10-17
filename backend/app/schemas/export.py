from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class ExportCreateRequest(BaseModel):
    format: str = Field(default="pdf")
    page_size: str = Field(default="B5") # B5 (standard manga), A4, US Letter
    reading_direction: Optional[str] = None # None uses project default
    include_cover: bool = True
    print_ready: bool = False
    custom_title: Optional[str] = None

class ExportResponse(BaseModel):
    id: str
    project_id: str
    chapter_id: str
    format: str
    storage_key: str
    status: str
    settings: Dict[str, Any]
    download_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
