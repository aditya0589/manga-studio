from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User
from app.models.publishing import UsageRecord
from app.schemas.settings import ProviderStatusResponse, UsageRecordResponse
from app.api.dependencies import get_current_user

router = APIRouter(prefix="/settings", tags=["Settings"])

@router.get("/providers", response_model=ProviderStatusResponse)
async def get_provider_status(current_user: User = Depends(get_current_user)):
    return ProviderStatusResponse(
        openrouter_configured=settings.is_llm_configured,
        openrouter_model=settings.OPENROUTER_MODEL,
        openrouter_fallback_model=settings.OPENROUTER_FALLBACK_MODEL,
        cloudflare_configured=settings.is_image_provider_configured,
        cloudflare_image_model=settings.CLOUDFLARE_IMAGE_MODEL,
        storage_backend=settings.STORAGE_BACKEND,
        database_mode="sqlite" if "sqlite" in settings.DATABASE_URL else "postgresql",
        is_mock_mode=not (settings.is_llm_configured and settings.is_image_provider_configured)
    )

@router.get("/models")
async def get_available_models(current_user: User = Depends(get_current_user)):
    return {
        "llm_models": [
            {"id": "anthropic/claude-3.5-sonnet", "name": "Claude 3.5 Sonnet (Recommended)", "context": 200000},
            {"id": "meta-llama/llama-3.3-70b-instruct:free", "name": "Llama 3.3 70B (Free Tier)", "context": 128000},
            {"id": "google/gemini-2.0-flash-001", "name": "Gemini 2.0 Flash", "context": 1000000},
            {"id": "deepseek/deepseek-r1", "name": "DeepSeek R1", "context": 64000}
        ],
        "image_models": [
            {"id": "@cf/black-forest-labs/flux-1-schnell", "name": "Flux 1 Schnell (Cloudflare Workers AI)", "type": "text-to-image"},
            {"id": "@cf/stabilityai/stable-diffusion-xl-base-1.0", "name": "SDXL Base 1.0", "type": "text-to-image"}
        ]
    }

@router.get("/usage", response_model=List[UsageRecordResponse])
async def get_usage_records(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(UsageRecord).where(UsageRecord.user_id == current_user.id).order_by(UsageRecord.created_at.desc()).limit(100)
    res = await db.execute(stmt)
    records = res.scalars().all()
    return [UsageRecordResponse.model_validate(r) for r in records]
