import json
import re
import asyncio
import random
from typing import Dict, Any, Optional, List
import httpx

from app.core.config import settings
from app.core.logging import logger
from app.providers.llm_base import BaseLLMProvider

class CloudflareLLMProvider(BaseLLMProvider):
    """
    Cloudflare Workers AI LLM Provider.
    Leverages fast, zero-marginal-cost models like @cf/meta/llama-3.1-8b-instruct
    to direct authentic story-driven manga scenes, beats, character profiles, and panel scripts.
    """
    DEFAULT_MODEL = "@cf/meta/llama-3.1-8b-instruct"

    def __init__(
        self,
        account_id: Optional[str] = None,
        api_token: Optional[str] = None,
        model: Optional[str] = None
    ):
        self.account_id = account_id or settings.CLOUDFLARE_ACCOUNT_ID
        self.api_token = api_token or settings.CLOUDFLARE_API_TOKEN
        self.model = model or getattr(settings, "CLOUDFLARE_LLM_MODEL", self.DEFAULT_MODEL)
        self.max_retries = 2
        self.timeout = 65.0

    @property
    def api_url(self) -> str:
        clean_model = self.model.lstrip("/")
        return f"https://api.cloudflare.com/client/v4/accounts/{self.account_id}/ai/run/{clean_model}"

    def _extract_json(self, text: str) -> Optional[dict]:
        """Safely extract JSON from raw markdown or text responses."""
        if not text:
            return None
        text = text.strip()
        # Direct parse attempt
        try:
            return json.loads(text)
        except Exception:
            pass

        # Try parsing markdown code block ```json ... ```
        json_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
        if json_match:
            try:
                return json.loads(json_match.group(1).strip())
            except Exception:
                pass

        # Try finding outer braces { ... }
        brace_match = re.search(r"\{[\s\S]*\}", text)
        if brace_match:
            try:
                return json.loads(brace_match.group(0))
            except Exception:
                pass

        return None

    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        response_format_json: bool = False
    ) -> Dict[str, Any]:
        if not self.account_id or not self.api_token:
            return {
                "content": "",
                "parsed_json": None,
                "model_used": self.model,
                "provider": "cloudflare",
                "tokens_used": 0,
                "success": False,
                "error": "Cloudflare account ID or API token not configured."
            }

        sys_msg = system_prompt or "You are an expert manga screenwriter and director. Structure dynamic visual storytelling with continuous narrative flow."
        if response_format_json and "JSON" not in sys_msg:
            sys_msg += " Output STRICT, valid JSON only. Do not wrap in conversational preamble."

        messages = [
            {"role": "system", "content": sys_msg},
            {"role": "user", "content": prompt}
        ]

        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }

        payload = {
            "messages": messages,
            "temperature": max(0.1, min(temperature, 1.0)),
            "max_tokens": max_tokens,
        }

        last_error = None
        async with httpx.AsyncClient() as client:
            for attempt in range(self.max_retries + 1):
                try:
                    logger.info(f"Cloudflare LLM calling {self.model} (attempt {attempt + 1})")
                    res = await client.post(
                        self.api_url,
                        headers=headers,
                        json=payload,
                        timeout=self.timeout
                    )

                    if res.status_code == 200:
                        data = res.json()
                        result = data.get("result", {})
                        raw_resp = result.get("response")
                        if isinstance(raw_resp, dict):
                            content = json.dumps(raw_resp)
                            parsed = raw_resp
                        elif isinstance(raw_resp, list):
                            content = json.dumps(raw_resp)
                            parsed = raw_resp
                        else:
                            content = str(raw_resp or "").strip()
                            parsed = None
                            if response_format_json or "{" in content:
                                parsed = self._extract_json(content)

                        return {
                            "content": content,
                            "parsed_json": parsed,
                            "model_used": self.model,
                            "provider": "cloudflare",
                            "tokens_used": len(content.split()),
                            "success": True,
                            "error": None
                        }
                    elif res.status_code in (429, 500, 502, 503, 504):
                        wait_time = (2 ** attempt) + random.uniform(0.5, 1.5)
                        logger.warning(f"Cloudflare LLM HTTP {res.status_code}, retrying in {wait_time:.1f}s")
                        await asyncio.sleep(wait_time)
                        last_error = f"HTTP {res.status_code}: {res.text}"
                    else:
                        last_error = f"HTTP {res.status_code}: {res.text}"
                        logger.error(f"Cloudflare LLM error: {last_error}")
                        break

                except (httpx.TimeoutException, httpx.RequestError) as e:
                    wait_time = (2 ** attempt) + random.uniform(0.5, 1.5)
                    logger.warning(f"Cloudflare LLM network/timeout: {e}. Retrying in {wait_time:.1f}s")
                    await asyncio.sleep(wait_time)
                    last_error = str(e)

        logger.error(f"Cloudflare LLM all retries failed: {last_error}")
        return {
            "content": "",
            "parsed_json": None,
            "model_used": self.model,
            "provider": "cloudflare",
            "tokens_used": 0,
            "success": False,
            "error": last_error or "Cloudflare LLM request failed."
        }
