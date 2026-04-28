from datetime import datetime
from typing import Any

import httpx

from app.config import Settings


class LokiClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def query_range(
        self,
        query: str,
        start: datetime,
        end: datetime,
        limit: int = 500,
        direction: str = "backward",
    ) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.settings.loki_timeout_seconds) as client:
            response = await client.get(
                f"{self.settings.loki_url}/loki/api/v1/query_range",
                params={
                    "query": query,
                    "start": str(int(start.timestamp() * 1_000_000_000)),
                    "end": str(int(end.timestamp() * 1_000_000_000)),
                    "limit": limit,
                    "direction": direction,
                },
            )
        response.raise_for_status()
        return response.json()
