import os
import hashlib
from typing import Optional
from pathlib import Path
from app.core.config import settings
from app.storage.base import StorageAdapter

class LocalStorageAdapter(StorageAdapter):
    def __init__(self, root_dir: Optional[str] = None):
        self.root_dir = Path(root_dir or settings.MEDIA_ROOT).resolve()
        self.root_dir.mkdir(parents=True, exist_ok=True)

    def _resolve_safe_path(self, key: str) -> Path:
        # Strip leading slashes to prevent root traversal
        clean_key = key.lstrip("/\\")
        target_path = (self.root_dir / clean_key).resolve()
        # Prevent directory traversal attacks
        if not str(target_path).startswith(str(self.root_dir)):
            raise ValueError("Path traversal attempt detected")
        return target_path

    async def save(self, file_data: bytes, key: str, content_type: str = "application/octet-stream") -> str:
        target_path = self._resolve_safe_path(key)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        with open(target_path, "wb") as f:
            f.write(file_data)
        return key

    async def get(self, key: str) -> Optional[bytes]:
        try:
            target_path = self._resolve_safe_path(key)
            if not target_path.exists():
                return None
            with open(target_path, "rb") as f:
                return f.read()
        except Exception:
            return None

    async def delete(self, key: str) -> bool:
        try:
            target_path = self._resolve_safe_path(key)
            if target_path.exists():
                target_path.unlink()
                return True
            return False
        except Exception:
            return False

    def get_url(self, key: str) -> str:
        # Returns API media endpoint url
        clean_key = key.lstrip("/\\").replace("\\", "/")
        return f"{settings.API_BASE_URL}/api/v1/assets/media/{clean_key}"

    def get_absolute_path(self, key: str) -> str:
        return str(self._resolve_safe_path(key))

def compute_checksum(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

storage: StorageAdapter = LocalStorageAdapter()
