from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = Field(default="Moonhub MCP Server", alias="APP_NAME")
    app_env: str = Field(default="dev", alias="APP_ENV")
    app_debug: bool = Field(default=False, alias="APP_DEBUG")

    clickhouse_url: str = Field(default="", alias="CLICKHOUSE_URL")
    clickhouse_user: str = Field(default="", alias="CLICKHOUSE_USER")
    clickhouse_password: str = Field(default="", alias="CLICKHOUSE_PASSWORD")
    clickhouse_database: str = Field(default="", alias="CLICKHOUSE_DATABASE")
    clickhouse_timeout_seconds: float = Field(default=30.0, alias="CLICKHOUSE_TIMEOUT_SECONDS")
    chat_log_table: str = Field(default="", alias="CHAT_LOG_TABLE")
    security_log_table: str = Field(default="", alias="SECURITY_LOG_TABLE")

    loki_url: str = Field(default="", alias="LOKI_URL")
    loki_timeout_seconds: float = Field(default=30.0, alias="LOKI_TIMEOUT_SECONDS")
    loki_app_label: str = Field(default="", alias="LOKI_APP_LABEL")
    loki_container_apps: str = Field(
        default="",
        alias="LOKI_CONTAINER_APPS",
    )
    loki_system_apps: str = Field(
        default="",
        alias="LOKI_SYSTEM_APPS",
    )

    prometheus_url: str = Field(default="", alias="PROMETHEUS_URL")
    prometheus_timeout_seconds: float = Field(default=30.0, alias="PROMETHEUS_TIMEOUT_SECONDS")
    prometheus_node_job: str = Field(default="", alias="PROMETHEUS_NODE_JOB")
    prometheus_node_instance: str = Field(default="", alias="PROMETHEUS_NODE_INSTANCE")
    prometheus_node_name: str = Field(default="", alias="PROMETHEUS_NODE_NAME")
    prometheus_service_job: str = Field(default="", alias="PROMETHEUS_SERVICE_JOB")
    prometheus_service_instance: str = Field(default="", alias="PROMETHEUS_SERVICE_INSTANCE")
    prometheus_service_application: str = Field(default="", alias="PROMETHEUS_SERVICE_APPLICATION")

    gemini_api_key: str = Field(default="", alias="GEMINI_API_KEY")
    gemini_model: str = Field(default="gemini-2.5-flash", alias="GEMINI_MODEL")

    prompt_chat_analysis: str = Field(default="", alias="PROMPT_CHAT_ANALYSIS")
    prompt_incident_analysis: str = Field(default="", alias="PROMPT_INCIDENT_ANALYSIS")
    prompt_security_analysis: str = Field(default="", alias="PROMPT_SECURITY_ANALYSIS")

    mysql_enabled: bool = Field(default=False, alias="MYSQL_ENABLED")
    mysql_host: str = Field(default="", alias="MYSQL_HOST")
    mysql_port: int = Field(default=3306, alias="MYSQL_PORT")
    mysql_user: str = Field(default="", alias="MYSQL_USER")
    mysql_password: str = Field(default="", alias="MYSQL_PASSWORD")
    mysql_database: str = Field(default="", alias="MYSQL_DATABASE")
    mysql_timeout_seconds: int = Field(default=10, alias="MYSQL_TIMEOUT_SECONDS")


@lru_cache
def get_settings() -> Settings:
    return Settings()
