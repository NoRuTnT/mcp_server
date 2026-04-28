import asyncio
from typing import Any

import pymysql

from app.config import Settings


class MySQLClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def query_select(self, sql: str, params: tuple[Any, ...] | None = None) -> list[dict[str, Any]]:
        normalized = sql.strip().lower()
        if not normalized.startswith("select"):
            raise ValueError("Only SELECT queries are allowed.")

        return await asyncio.to_thread(self._query_sync, sql, params or ())

    def _query_sync(self, sql: str, params: tuple[Any, ...]) -> list[dict[str, Any]]:
        conn = pymysql.connect(
            host=self.settings.mysql_host,
            port=self.settings.mysql_port,
            user=self.settings.mysql_user,
            password=self.settings.mysql_password,
            database=self.settings.mysql_database,
            connect_timeout=self.settings.mysql_timeout_seconds,
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True,
        )
        try:
            with conn.cursor() as cursor:
                cursor.execute(sql, params)
                return cursor.fetchall()
        finally:
            conn.close()
