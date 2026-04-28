from dataclasses import dataclass

from app.clients.clickhouse import ClickHouseClient
from app.clients.gemini_client import GeminiClient
from app.clients.loki import LokiClient
from app.clients.mysql import MySQLClient
from app.clients.prometheus import PrometheusClient
from app.config import Settings, get_settings


@dataclass
class AnalysisDependencies:
    settings: Settings
    clickhouse: ClickHouseClient
    prometheus: PrometheusClient
    loki: LokiClient
    gemini: GeminiClient
    mysql: MySQLClient


def get_analysis_dependencies() -> AnalysisDependencies:
    settings = get_settings()
    return AnalysisDependencies(
        settings=settings,
        clickhouse=ClickHouseClient(settings),
        prometheus=PrometheusClient(settings),
        loki=LokiClient(settings),
        gemini=GeminiClient(settings),
        mysql=MySQLClient(settings),
    )
