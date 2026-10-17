from abc import ABC, abstractmethod
from typing import Optional, BinaryIO

class StorageAdapter(ABC):
    @abstractmethod
    async def save(self, file_data: bytes, key: str, content_type: str = "application/octet-stream") -> str:
        """Save binary data to storage and return the storage key."""
        pass

    @abstractmethod
    async def get(self, key: str) -> Optional[bytes]:
        """Retrieve binary data from storage by key."""
        pass

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete an object from storage by key."""
        pass

    @abstractmethod
    def get_url(self, key: str) -> str:
        """Return the URL or endpoint to access the resource."""
        pass

    @abstractmethod
    def get_absolute_path(self, key: str) -> str:
        """Return the absolute path on disk if local storage."""
        pass
