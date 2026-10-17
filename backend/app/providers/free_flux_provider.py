import random
import urllib.parse
import urllib.request
import ssl
import asyncio
from typing import Dict, Any, Optional

from app.core.logging import logger
from app.providers.image_base import BaseImageProvider

# Manga-specific style blueprints for high-quality output
_MANGA_STYLE_TAGS = {
    "bw": (
        "masterpiece manga panel, traditional Japanese manga art style, "
        "crisp clean ink linework, bold outlines, heavy black shadows, "
        "detailed screentone dot patterns, dynamic hatching cross-hatching, "
        "high contrast monochrome, professional manga illustration, "
        "Kentaro Miura art style, Takehiko Inoue ink style, "
        "dramatic composition, expressive character faces, "
        "manga panel borders"
    ),
    "anime_color": (
        "masterpiece anime illustration, vibrant saturated colors, "
        "detailed cel shading, soft ambient occlusion, "
        "Makoto Shinkai lighting, Studio Ghibli quality backgrounds, "
        "sharp clean anime lineart, dynamic poses, expressive emotions"
    ),
    "dark_fantasy": (
        "masterpiece dark manga panel, Berserk art style, "
        "heavy inking, dramatic chiaroscuro, deep shadows, "
        "grim detailed crosshatching, horror fantasy atmosphere, "
        "intricate armor and weapon details, intense emotion"
    ),
    "cyberpunk": (
        "masterpiece cyberpunk manga panel, Ghost in the Shell aesthetic, "
        "neo-tokyo neon-lit streets, intricate tech linework, "
        "detailed mech designs, dynamic perspective, "
        "sharp clean manga inking, futuristic atmosphere"
    ),
    "shonen": (
        "masterpiece shonen manga panel, Dragon Ball Z energy auras, "
        "speed lines motion blur, explosive action poses, "
        "bold exclamation expressions, dynamic camera angles, "
        "clean bold ink outlines, screentone shading"
    ),
}

_NEGATIVE_PROMPT = (
    "photo, photorealistic, 3d render, western comic, cartoon, chibi, "
    "low quality, blurry, watermark, text overlay, speech bubbles in image, "
    "dialogue, typography, words in image, letter, ugly, deformed, "
    "extra limbs, bad anatomy, nsfw, nude, extra fingers"
)


class FreeFluxImageProvider(BaseImageProvider):
    """
    Zero-key public FLUX / Manga generation provider using Pollinations AI.
    Upgraded with manga-specialist prompt engineering for authentic results.
    """
    def __init__(self, model: str = "flux", timeout: int = 75):
        self.model = model
        self.timeout = timeout

    def _detect_style_key(self, art_style: str, genre: str = "") -> str:
        combined = (art_style + " " + genre).lower()
        if "dark fantasy" in combined or "berserk" in combined or "noir" in combined or "horror" in combined:
            return "dark_fantasy"
        if "cyberpunk" in combined or "cyber" in combined or "sci-fi" in combined or "scifi" in combined:
            return "cyberpunk"
        if "shonen" in combined or "action" in combined or "battle" in combined or "fighting" in combined:
            return "shonen"
        if "color" in combined or "anime" in combined or "color" in combined:
            return "anime_color"
        return "bw"

    def _build_full_prompt(
        self,
        prompt: str,
        art_style: str,
        canonical_descriptions: Optional[str] = None,
        genre: str = "",
    ) -> str:
        style_key = self._detect_style_key(art_style, genre)
        style_tags = _MANGA_STYLE_TAGS[style_key]

        # Core scene description — keep up to 350 chars for richer context
        clean_prompt = prompt.strip()[:350]

        # Build character anchor
        char_tag = ""
        if canonical_descriptions:
            # Truncate and clean character descriptions
            char_clean = canonical_descriptions.strip()[:200]
            char_tag = f"Character design: {char_clean}. "

        # Assemble final prompt — quality tokens first for best influence
        full = (
            f"{style_tags}. "
            f"{char_tag}"
            f"Scene: {clean_prompt}. "
            f"No text, no speech bubbles, no watermarks."
        )
        return full

    def _fetch_sync(self, url: str) -> Optional[bytes]:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0.0.0 Safari/537.36"
                )
            }
        )
        ctx = ssl.create_default_context()
        with urllib.request.urlopen(req, timeout=self.timeout, context=ctx) as resp:
            if resp.status == 200:
                data = resp.read()
                content_type = resp.headers.get("Content-Type", "")
                if "text/html" not in content_type and len(data) > 1000:
                    return data
        return None

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
        full_prompt = self._build_full_prompt(prompt, art_style, canonical_descriptions, genre)
        neg = negative_prompt or _NEGATIVE_PROMPT

        encoded_prompt = urllib.parse.quote(full_prompt)
        encoded_neg = urllib.parse.quote(neg)
        seed = random.randint(10000, 9999999)

        logger.info(f"Free FLUX Provider — style prompt (first 120): {full_prompt[:120]}...")

        last_error = None
        for attempt in range(2):
            # Use the 'flux' model which gives the best manga-quality output on Pollinations
            current_url = (
                f"https://image.pollinations.ai/prompt/{encoded_prompt}"
                f"?width={width}&height={height}"
                f"&nologo=true"
                f"&seed={seed + attempt * 37}"
                f"&model=flux"
                f"&negative_prompt={encoded_neg}"
                f"&enhance=true"
            )
            try:
                img_data = await asyncio.to_thread(self._fetch_sync, current_url)
                if img_data:
                    logger.info(
                        f"Free FLUX generated {len(img_data)} bytes of manga artwork "
                        f"(attempt {attempt + 1})."
                    )
                    return {
                        "image_bytes": img_data,
                        "mime_type": "image/jpeg",
                        "width": width,
                        "height": height,
                        "model_used": "free-flux-manga",
                        "provider": "free_flux",
                        "success": True,
                        "error": None
                    }
            except Exception as e:
                err_str = str(e)
                if hasattr(e, "read"):
                    try:
                        err_str += " " + e.read().decode("utf-8", errors="ignore")
                    except Exception:
                        pass
                logger.warning(f"Free FLUX attempt {attempt + 1} failed: {err_str[:200]}")
                last_error = err_str

                if "402" in err_str or "FREE_LIMIT" in err_str or "Payment Required" in err_str:
                    import re
                    match = re.search(r"Retry after (\d+)s", err_str)
                    wait_sec = (int(match.group(1)) + 1) if match else 46
                    if attempt == 0:
                        logger.info(
                            f"Free tier IP cooldown: waiting {wait_sec}s before auto-retry..."
                        )
                        await asyncio.sleep(wait_sec)
                        continue
                    else:
                        last_error = (
                            f"Free tier limit (1 image every 45s). "
                            f"Please wait {wait_sec}s before regenerating."
                        )
                else:
                    await asyncio.sleep(4)

        logger.error(f"Free FLUX generation failed after retries: {last_error}")
        return {
            "image_bytes": None,
            "mime_type": "image/jpeg",
            "width": width,
            "height": height,
            "model_used": "free-flux-manga",
            "provider": "free_flux",
            "success": False,
            "error": last_error or "Image generation failed. Please try again in 45 seconds."
        }
