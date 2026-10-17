import os
from pathlib import Path
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
DEFAULT_DB_PATH = (BACKEND_DIR / "manga_studio.db").as_posix()

class Settings(BaseSettings):
    APP_ENV: str = "development"
    APP_SECRET_KEY: str = "dev_secret_key_manga_studio_super_secure_change_in_prod_123456"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    FRONTEND_URL: str = "http://localhost:5173"
    API_BASE_URL: str = "http://localhost:8000"
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]

    DATABASE_URL: str = f"sqlite+aiosqlite:///{DEFAULT_DB_PATH}"
    REDIS_URL: str = "redis://localhost:6379/0"

    # AI Providers
    OPENROUTER_API_KEY: Optional[str] = None
    OPENROUTER_MODEL: str = "anthropic/claude-3.5-sonnet"
    OPENROUTER_FALLBACK_MODEL: str = "meta-llama/llama-3.3-70b-instruct:free"

    CLOUDFLARE_ACCOUNT_ID: Optional[str] = None
    CLOUDFLARE_API_TOKEN: Optional[str] = None
    CLOUDFLARE_IMAGE_MODEL: str = "@cf/black-forest-labs/flux-1-schnell"
    CLOUDFLARE_LLM_MODEL: str = "@cf/meta/llama-3.1-8b-instruct"

    # Storage
    STORAGE_BACKEND: str = "local"
    MEDIA_ROOT: str = "./media"

    # Limits and constraints
    MAX_UPLOAD_SIZE_MB: int = 20
    MAX_PAGES_PER_CHAPTER: int = 20
    MAX_IMAGE_RETRIES: int = 2
    MAX_CONCURRENT_IMAGE_JOBS: int = 2

    # Free tier / Cost limits
    DAILY_REQUEST_LIMIT: int = 100
    MONTHLY_REQUEST_LIMIT: int = 2000

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def resolved_database_url(self) -> str:
        if "sqlite" in self.DATABASE_URL and ":///" in self.DATABASE_URL:
            # If relative path like sqlite+aiosqlite:///./manga_studio.db or sqlite+aiosqlite:///manga_studio.db
            prefix, path_part = self.DATABASE_URL.split(":///", 1)
            if path_part.startswith("./"):
                abs_path = (BACKEND_DIR / path_part[2:]).as_posix()
                return f"{prefix}:///{abs_path}"
            elif not os.path.isabs(path_part) and not (len(path_part) > 1 and path_part[1] == ':'):
                abs_path = (BACKEND_DIR / path_part).as_posix()
                return f"{prefix}:///{abs_path}"
        return self.DATABASE_URL

    @property
    def is_llm_configured(self) -> bool:
        return bool(
            (self.OPENROUTER_API_KEY and self.OPENROUTER_API_KEY.strip()) or
            (self.CLOUDFLARE_ACCOUNT_ID and self.CLOUDFLARE_ACCOUNT_ID.strip() and self.CLOUDFLARE_API_TOKEN and self.CLOUDFLARE_API_TOKEN.strip())
        )

    @property
    def is_image_provider_configured(self) -> bool:
        return bool(
            self.CLOUDFLARE_ACCOUNT_ID and self.CLOUDFLARE_ACCOUNT_ID.strip() and
            self.CLOUDFLARE_API_TOKEN and self.CLOUDFLARE_API_TOKEN.strip()
        )

settings = Settings()
