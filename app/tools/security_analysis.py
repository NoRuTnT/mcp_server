import asyncio

from app.mcp.deps import AnalysisDependencies
from app.schemas.security import SecurityRiskRequest, SecurityRiskResponse
from app.services.prompt_builder import build_security_analysis_prompt


async def analyze_security_risks(
    request: SecurityRiskRequest,
    deps: AnalysisDependencies,
) -> SecurityRiskResponse:
    failed_login_sql = f"""
    SELECT
      sourceIp,
      count(*) AS failedCount,
      min(timestamp) AS firstSeen,
      max(timestamp) AS lastSeen
    FROM {deps.settings.security_log_table}
    WHERE timestamp >= now() - INTERVAL {request.days} DAY
      AND eventType IN ('LOGIN_FAILED', 'AUTH_FAILED')
    GROUP BY sourceIp
    HAVING failedCount >= 5
    ORDER BY failedCount DESC
    LIMIT 50
    """

    suspicious_path_sql = f"""
    SELECT
      path,
      sourceIp,
      status,
      count(*) AS cnt
    FROM {deps.settings.security_log_table}
    WHERE timestamp >= now() - INTERVAL {request.days} DAY
      AND (
        positionCaseInsensitive(path, 'wp-admin') > 0
        OR positionCaseInsensitive(path, '.env') > 0
        OR positionCaseInsensitive(path, 'phpmyadmin') > 0
        OR positionCaseInsensitive(path, '/admin') > 0
        OR positionCaseInsensitive(path, '../') > 0
      )
    GROUP BY path, sourceIp, status
    ORDER BY cnt DESC
    LIMIT 100
    """

    abnormal_status_sql = f"""
    SELECT
      status,
      count(*) AS cnt
    FROM {deps.settings.security_log_table}
    WHERE timestamp >= now() - INTERVAL {request.days} DAY
      AND status IN (401, 403, 404, 429, 500)
    GROUP BY status
    ORDER BY cnt DESC
    """

    failed_logins, suspicious_paths, abnormal_statuses = await asyncio.gather(
        deps.clickhouse.query_select(failed_login_sql),
        deps.clickhouse.query_select(suspicious_path_sql),
        deps.clickhouse.query_select(abnormal_status_sql),
    )

    summary = await deps.gemini.summarize(
        build_security_analysis_prompt(deps.settings),
        {
            "days": request.days,
            "failedLogins": failed_logins,
            "suspiciousPaths": suspicious_paths,
            "abnormalStatuses": abnormal_statuses,
        },
    )

    return SecurityRiskResponse(
        days=request.days,
        failed_login_sources=len(failed_logins),
        suspicious_path_count=len(suspicious_paths),
        summary=summary,
    )
