import json
from typing import Any

import httpx

from app.config import Settings


class ClickHouseClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def query_select(self, sql: str) -> list[dict[str, Any]]:
        normalized = sql.strip().lower()
        if not normalized.startswith("select"):
            raise ValueError("Only SELECT queries are allowed.")

        async with httpx.AsyncClient(timeout=self.settings.clickhouse_timeout_seconds) as client:
            response = await client.post(
                f"{self.settings.clickhouse_url}/",
                params={
                    "database": self.settings.clickhouse_database,
                    "default_format": "JSONEachRow",
                },
                auth=(self.settings.clickhouse_user, self.settings.clickhouse_password),
                content=sql.encode("utf-8"),
            )

        response.raise_for_status()

        rows: list[dict[str, Any]] = []
        for line in response.text.splitlines():
            if line.strip():
                rows.append(json.loads(line))
        return rows
