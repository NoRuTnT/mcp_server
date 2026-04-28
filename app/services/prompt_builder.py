from app.config import Settings


def _require_prompt(value: str, env_name: str) -> str:
    normalized = value.replace("\\n", "\n").strip()
    if not normalized:
        raise ValueError(f"{env_name} must be set in .env")
    return normalized


def build_chat_analysis_prompt(settings: Settings) -> str:
    return _require_prompt(settings.prompt_chat_analysis, "PROMPT_CHAT_ANALYSIS")


def build_incident_analysis_prompt(settings: Settings) -> str:
    return _require_prompt(settings.prompt_incident_analysis, "PROMPT_INCIDENT_ANALYSIS")


def build_security_analysis_prompt(settings: Settings) -> str:
    return _require_prompt(settings.prompt_security_analysis, "PROMPT_SECURITY_ANALYSIS")
