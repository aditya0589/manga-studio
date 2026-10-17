from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel

class ProviderStatusResponse(BaseModel):
    openrouter_configured: bool
    openrouter_model: str
    openrouter_fallback_model: str
    cloudflare_configured: bool
    cloudflare_image_model: str
    storage_backend: str
    database_mode: str
    is_mock_mode: bool

class UsageRecordResponse(BaseModel):
    id: str
    user_id: str
    project_id: Optional[str]
    provider: str
    model: str
    operation: str
    request_count: int
    estimated_cost: float
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
