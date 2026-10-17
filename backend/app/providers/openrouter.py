import json
import re
import asyncio
import random
from typing import Dict, Any, Optional
import httpx

from app.core.config import settings
from app.core.logging import logger
from app.providers.llm_base import BaseLLMProvider

class OpenRouterProvider(BaseLLMProvider):
    API_URL = "https://openrouter.ai/api/v1/chat/completions"

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        fallback_model: Optional[str] = None
    ):
        self.api_key = api_key or settings.OPENROUTER_API_KEY
        self.model = model or settings.OPENROUTER_MODEL
        self.fallback_model = fallback_model or settings.OPENROUTER_FALLBACK_MODEL
        self.max_retries = 2
        self.timeout = 60.0

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

        # Try parsing code block ```json ... ```
        json_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
        if json_match:
            try:
                return json.loads(json_match.group(1))
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

    async def _make_request(
        self,
        client: httpx.AsyncClient,
        model: str,
        messages: list,
        temperature: float,
        max_tokens: int,
        response_format_json: bool
    ) -> httpx.Response:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": settings.FRONTEND_URL,
            "X-Title": "AI Manga Studio",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        if response_format_json:
            payload["response_format"] = {"type": "json_object"}

        response = await client.post(
            self.API_URL,
            headers=headers,
            json=payload,
            timeout=self.timeout
        )
        return response

    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2500,
        response_format_json: bool = False
    ) -> Dict[str, Any]:
        if not self.api_key:
            return {
                "content": "",
                "parsed_json": None,
                "model_used": "none",
                "provider": "openrouter",
                "tokens_used": 0,
                "success": False,
                "error": "OpenRouter API key is not configured. Please supply OPENROUTER_API_KEY in settings or .env"
            }

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        models_to_try = [self.model]
        if self.fallback_model and self.fallback_model != self.model:
            models_to_try.append(self.fallback_model)

        last_error = None
        async with httpx.AsyncClient() as client:
            for current_model in models_to_try:
                for attempt in range(self.max_retries + 1):
                    try:
                        logger.info(f"OpenRouter calling model {current_model} (attempt {attempt + 1})")
                        res = await self._make_request(
                            client, current_model, messages, temperature, max_tokens, response_format_json
                        )

                        if res.status_code == 200:
                            data = res.json()
                            content = data["choices"][0]["message"]["content"]
                            tokens_used = data.get("usage", {}).get("total_tokens", 0)
                            parsed_json = self._extract_json(content) if response_format_json else None

                            return {
                                "content": content,
                                "parsed_json": parsed_json,
                                "model_used": current_model,
                                "provider": "openrouter",
                                "tokens_used": tokens_used,
                                "success": True,
                                "error": None
                            }
                        elif res.status_code in (429, 502, 503, 504):
                            wait_time = (2 ** attempt) + random.uniform(0.5, 1.5)
                            logger.warning(f"OpenRouter rate limit or server error ({res.status_code}), backing off for {wait_time:.1f}s")
                            await asyncio.sleep(wait_time)
                            last_error = f"HTTP {res.status_code}: {res.text}"
                        else:
                            last_error = f"HTTP {res.status_code}: {res.text}"
                            logger.error(f"OpenRouter request error: {last_error}")
                            break # Don't retry client errors (400, 401, etc.) on same model

                    except (httpx.TimeoutException, httpx.RequestError) as e:
                        wait_time = (2 ** attempt) + random.uniform(0.5, 1.5)
                        logger.warning(f"OpenRouter network timeout/error: {e}. Retrying in {wait_time:.1f}s")
                        await asyncio.sleep(wait_time)
                        last_error = str(e)

        return {
            "content": "",
            "parsed_json": None,
            "model_used": models_to_try[0],
            "provider": "openrouter",
            "tokens_used": 0,
            "success": False,
            "error": f"OpenRouter calls failed after retries: {last_error}"
        }
