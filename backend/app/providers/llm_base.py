from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List

class BaseLLMProvider(ABC):
    @abstractmethod
    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        response_format_json: bool = False
    ) -> Dict[str, Any]:
        """
        Generate text or JSON response.
        Returns a dict:
        {
            "content": str,
            "parsed_json": Optional[dict],
            "model_used": str,
            "provider": str,
            "tokens_used": int,
            "success": bool,
            "error": Optional[str]
        }
        """
        pass
