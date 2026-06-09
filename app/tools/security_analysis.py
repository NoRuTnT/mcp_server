from datetime import timedelta

from app.mcp.deps import AnalysisDependencies
from app.schemas.security import SecurityRiskRequest, SecurityRiskResponse
from app.services.log_formatter import flatten_loki_streams, summarize_loki_apps
from app.services.log_query_builder import build_loki_security_query
from app.services.prompt_builder import build_security_analysis_prompt
from app.services.time_range import recent_utc_window


async def analyze_security_risks(
    request: SecurityRiskRequest,
    deps: AnalysisDependencies,
) -> SecurityRiskResponse:
    end = recent_utc_window(0)[1]
    start = end - timedelta(days=request.days)
    security_app_names = [
        app.strip()
        for app in deps.settings.loki_security_apps.split(",")
        if app.strip()
    ]
    if not security_app_names:
        raise ValueError("LOKI_SECURITY_APPS must be set in .env")
    loki_query = build_loki_security_query(deps.settings.loki_app_label, security_app_names)
    loki_payload = await deps.loki.query_range(
        query=loki_query,
        start=start,
        end=end,
        limit=1000,
    )
    security_logs = flatten_loki_streams(loki_payload, deps.settings.loki_app_label)
    source_counts = summarize_loki_apps(security_logs)

    summary = await deps.gemini.summarize(
        build_security_analysis_prompt(deps.settings),
        {
            "days": request.days,
            "lokiQuery": loki_query,
            "securityLogs": security_logs,
            "logSourceCounts": source_counts,
        },
    )

    return SecurityRiskResponse(
        days=request.days,
        failed_login_sources=len(source_counts),
        suspicious_path_count=len(security_logs),
        summary=summary,
    )
