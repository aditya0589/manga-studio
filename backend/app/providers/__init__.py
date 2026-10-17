from app.core.config import settings
from app.providers.llm_base import BaseLLMProvider
from app.providers.image_base import BaseImageProvider
from app.providers.openrouter import OpenRouterProvider
from app.providers.cloudflare_ai import CloudflareAIProvider
from app.providers.cloudflare_llm import CloudflareLLMProvider
from app.providers.free_flux_provider import FreeFluxImageProvider
from app.providers.mock_provider import MockLLMProvider, MockImageProvider

import os

def get_llm_provider(force_mock: bool = False) -> BaseLLMProvider:
    if force_mock or os.getenv("TESTING") == "1":
        return MockLLMProvider()
    if settings.OPENROUTER_API_KEY and settings.OPENROUTER_API_KEY.strip():
        return OpenRouterProvider()
    if settings.is_image_provider_configured:
        return CloudflareLLMProvider()
    return MockLLMProvider()

def get_image_provider(force_mock: bool = False) -> BaseImageProvider:
    if force_mock or os.getenv("TESTING") == "1":
        return MockImageProvider()
    if settings.is_image_provider_configured:
        return CloudflareAIProvider()
    # Default to Free Real FLUX AI Engine for interactive creative studio usage!
    return FreeFluxImageProvider()

__all__ = [
    "BaseLLMProvider",
    "BaseImageProvider",
    "OpenRouterProvider",
    "CloudflareAIProvider",
    "MockLLMProvider",
    "MockImageProvider",
    "get_llm_provider",
    "get_image_provider"
]
