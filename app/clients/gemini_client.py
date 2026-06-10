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
        return await self.generate_text(prompt)

    async def generate_text(self, prompt: str) -> str:
        if not self._client:
            return self._fallback_summary(prompt)

        last_error: Exception | None = None
        for attempt in range(3):
            try:
                response = await asyncio.to_thread(
                    self._client.models.generate_content,
                    model=self.settings.gemini_model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.2,
                    ),
                )
                return response.text or ""
            except Exception as exc:
                last_error = exc
                if attempt < 2:
                    await asyncio.sleep(2**attempt)

        return (
            "Gemini API is temporarily unavailable, so the server could not generate "
            f"an AI summary. Error: {last_error}"
        )

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
