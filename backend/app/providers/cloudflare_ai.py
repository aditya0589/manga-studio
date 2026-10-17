import base64
import asyncio
import random
from typing import Dict, Any, Optional
import httpx

from app.core.config import settings
from app.core.logging import logger
from app.providers.image_base import BaseImageProvider

class CloudflareAIProvider(BaseImageProvider):
    def __init__(
        self,
        account_id: Optional[str] = None,
        api_token: Optional[str] = None,
        model: Optional[str] = None
    ):
        self.account_id = account_id or settings.CLOUDFLARE_ACCOUNT_ID
        self.api_token = api_token or settings.CLOUDFLARE_API_TOKEN
        self.model = model or settings.CLOUDFLARE_IMAGE_MODEL
        self.max_retries = settings.MAX_IMAGE_RETRIES
        self.timeout = 75.0

    @property
    def api_url(self) -> str:
        clean_model = self.model.lstrip("/")
        return f"https://api.cloudflare.com/client/v4/accounts/{self.account_id}/ai/run/{clean_model}"

    # Manga-specialist style blueprints
    _STYLE_MAP = {
        "bw": (
            "traditional Japanese manga panel, crisp bold ink linework, "
            "detailed screentone shading, high contrast monochrome, "
            "dramatic cinematic lighting"
        ),
        "dark_fantasy": (
            "dark fantasy manga panel, Berserk aesthetic, "
            "heavy chiaroscuro ink cross-hatching, deep shadows, "
            "grim dramatic atmosphere"
        ),
        "cyberpunk": (
            "cyberpunk manga panel, Ghost in the Shell aesthetic, "
            "intricate tech linework, neo-tokyo atmosphere, sharp manga inking"
        ),
        "shonen": (
            "dynamic shonen manga panel, bold ink lines, "
            "dramatic speedlines, explosive high-energy composition"
        ),
        "anime_color": (
            "vibrant anime comic illustration, detailed cel shading, "
            "clean anime lineart, atmospheric lighting"
        ),
    }

    _NEGATIVE_PROMPT = (
        "photo, photorealistic, 3d render, western cartoon, chibi, "
        "blurry, low quality, watermark, text overlay, dialogue bubbles in image, "
        "words in artwork, ugly, deformed, extra limbs, bad anatomy"
    )

    def _detect_style_key(self, art_style: str) -> str:
        s = art_style.lower()
        if "dark fantasy" in s or "berserk" in s or "noir" in s:
            return "dark_fantasy"
        if "cyberpunk" in s or "sci-fi" in s:
            return "cyberpunk"
        if "shonen" in s or "action" in s:
            return "shonen"
        if "color" in s or "anime" in s:
            return "anime_color"
        return "bw"

    def _build_full_prompt(
        self,
        prompt: str,
        art_style: str,
        canonical_descriptions: Optional[str] = None
    ) -> str:
        style_key = self._detect_style_key(art_style)
        style_tags = self._STYLE_MAP[style_key]

        # 1. Dynamic Shot angle, composition, action, and setting FIRST
        clean_prompt = prompt.strip().rstrip(".")

        # 2. Character visual anchors (if characters are present in this panel)
        char_tag = ""
        if canonical_descriptions and canonical_descriptions.strip():
            char_tag = f"Featuring {canonical_descriptions.strip().rstrip('.')}. "

        # 3. Assemble: [Cinematography & Action] -> [Character Consistency Anchors] -> [Art Style & Medium Guidance]
        full = (
            f"{clean_prompt}. "
            f"{char_tag}"
            f"Style: {style_tags}, professional manga illustration, "
            f"no text, no speech bubbles, no dialogue boxes, no watermark."
        )
        return full

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
        if not self.account_id or not self.api_token:
            return {
                "image_bytes": None,
                "mime_type": "image/jpeg",
                "width": width,
                "height": height,
                "model_used": self.model,
                "provider": "cloudflare",
                "success": False,
                "error": "Cloudflare account ID or API token is not configured. Supply CLOUDFLARE_ACCOUNT_ID and CLOUDFLARE_API_TOKEN in settings or .env"
            }

        full_prompt = self._build_full_prompt(prompt, art_style, canonical_descriptions)
        neg = negative_prompt or self._NEGATIVE_PROMPT
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        
        # Flux models on Cloudflare AI strictly enforce JSON schema:
        # only 'prompt', 'steps' (max 8), and 'image' are permitted
        if "flux" in self.model.lower():
            # Include negative guidance in prompt context for Flux prompt-steering
            flux_prompt = (
                f"{full_prompt}. "
                f"Negative guidance: photorealistic, 3d render, western cartoon, blurry, deformed anatomy, dialogue bubbles."
            )
            payload = {
                "prompt": flux_prompt,
                "steps": 6,
            }
        else:
            payload = {
                "prompt": full_prompt,
                "negative_prompt": neg,
                "num_steps": 8,
                "width": width,
                "height": height,
            }

        last_error = None
        async with httpx.AsyncClient() as client:
            for attempt in range(self.max_retries + 1):
                try:
                    logger.info(f"Cloudflare AI calling {self.model} (attempt {attempt + 1})")
                    res = await client.post(
                        self.api_url,
                        headers=headers,
                        json=payload,
                        timeout=self.timeout
                    )

                    if res.status_code == 200:
                        content_type = res.headers.get("content-type", "")
                        # Case 1: Raw binary image returned
                        if "image/" in content_type:
                            return {
                                "image_bytes": res.content,
                                "mime_type": content_type,
                                "width": width,
                                "height": height,
                                "model_used": self.model,
                                "provider": "cloudflare",
                                "success": True,
                                "error": None
                            }
                        # Case 2: JSON response with base64 image or result
                        try:
                            data = res.json()
                            if "result" in data and isinstance(data["result"], dict) and "image" in data["result"]:
                                img_data = base64.b64decode(data["result"]["image"])
                                return {
                                    "image_bytes": img_data,
                                    "mime_type": "image/jpeg",
                                    "width": width,
                                    "height": height,
                                    "model_used": self.model,
                                    "provider": "cloudflare",
                                    "success": True,
                                    "error": None
                                }
                            elif "errors" in data and data["errors"]:
                                last_error = str(data["errors"])
                        except Exception:
                            # Fallback if raw binary without image content-type
                            if len(res.content) > 1000:
                                return {
                                    "image_bytes": res.content,
                                    "mime_type": "image/jpeg",
                                    "width": width,
                                    "height": height,
                                    "model_used": self.model,
                                    "provider": "cloudflare",
                                    "success": True,
                                    "error": None
                                }

                    elif res.status_code in (429, 500, 502, 503, 504):
                        wait_time = (2 ** attempt) + random.uniform(0.5, 1.5)
                        logger.warning(f"Cloudflare AI HTTP {res.status_code}, retrying in {wait_time:.1f}s")
                        await asyncio.sleep(wait_time)
                        last_error = f"HTTP {res.status_code}: {res.text}"
                    else:
                        last_error = f"HTTP {res.status_code}: {res.text}"
                        logger.error(f"Cloudflare AI request error: {last_error}")
                        break

                except (httpx.TimeoutException, httpx.RequestError) as e:
                    wait_time = (2 ** attempt) + random.uniform(0.5, 1.5)
                    logger.warning(f"Cloudflare AI timeout/network error: {e}. Retrying in {wait_time:.1f}s")
                    await asyncio.sleep(wait_time)
                    last_error = str(e)

        return {
            "image_bytes": None,
            "mime_type": "image/jpeg",
            "width": width,
            "height": height,
            "model_used": self.model,
            "provider": "cloudflare",
            "success": False,
            "error": f"Cloudflare AI image generation failed: {last_error}"
        }
