import asyncio
import json
from typing import Any

from google import genai
from google.genai import types

from app.config import Settings


class GeminiClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._client = genai.Client(api_key=settings.gemini_api_key) if settings.gemini_api_key else None

    async def summarize(self, system_prompt: str, payload: Any) -> str:
        if not self._client:
            return self._fallback_summary(payload)

        prompt = self._build_prompt(system_prompt, payload)
        response = await asyncio.to_thread(
            self._client.models.generate_content,
            model=self.settings.gemini_model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.2,
                system_instruction=system_prompt,
            ),
        )
        return response.text or ""

    @staticmethod
    def _build_prompt(system_prompt: str, payload: Any) -> str:
        return (
            f"{system_prompt}\n\n"
            "[분석 대상 데이터]\n"
            f"{json.dumps(payload, ensure_ascii=False, default=str)}"
        )

    @staticmethod
    def _fallback_summary(payload: Any) -> str:
        size = len(payload) if isinstance(payload, list) else 1
        return (
            "GEMINI_API_KEY is not configured. "
            f"Fallback summary only. Input payload unit count: {size}."
        )
