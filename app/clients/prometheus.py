from datetime import datetime
from typing import Any

import httpx

from app.config import Settings


class PrometheusClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def query(self, query: str) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.settings.prometheus_timeout_seconds) as client:
            response = await client.get(
                f"{self.settings.prometheus_url}/api/v1/query",
                params={"query": query},
            )
        response.raise_for_status()
        return response.json()

    async def query_range(
        self,
        query: str,
        start: datetime,
        end: datetime,
        step: str = "60s",
    ) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.settings.prometheus_timeout_seconds) as client:
            response = await client.get(
                f"{self.settings.prometheus_url}/api/v1/query_range",
                params={
                    "query": query,
                    "start": int(start.timestamp()),
                    "end": int(end.timestamp()),
                    "step": step,
                },
            )
        response.raise_for_status()
        return response.json()
