from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseImageProvider(ABC):
    @abstractmethod
    async def generate_image(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        width: int = 768,
        height: int = 1024,
        art_style: str = "Traditional Manga B&W",
        canonical_descriptions: Optional[str] = None,
        genre: str = "",
    ) -> Dict[str, Any]:
        """
        Generate image binary.
        Args:
            prompt: Scene/action description (visual only, no dialogue).
            negative_prompt: Things to avoid in the image.
            width: Image width in pixels.
            height: Image height in pixels.
            art_style: Art direction string (e.g. 'Traditional Manga B&W', 'Dark Fantasy').
            canonical_descriptions: Character visual details for consistency.
            genre: Story genre for style detection (e.g. 'Action', 'Cyberpunk').
        Returns a dict:
        {
            "image_bytes": Optional[bytes],
            "mime_type": str,
            "width": int,
            "height": int,
            "model_used": str,
            "provider": str,
            "success": bool,
            "error": Optional[str]
        }
        """
        pass
