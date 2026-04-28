import asyncio

from app.mcp.deps import AnalysisDependencies
from app.schemas.incident import IncidentRequest, IncidentResponse
from app.services.log_formatter import flatten_loki_streams, summarize_loki_apps
from app.services.log_query_builder import build_loki_error_query
from app.services.prompt_builder import build_incident_analysis_prompt
from app.services.time_range import recent_utc_window


async def analyze_incident_last_minutes(
    request: IncidentRequest,
    deps: AnalysisDependencies,
) -> IncidentResponse:
    start, end = recent_utc_window(request.minutes)
    node_metric_labels = (
        f'job="{deps.settings.prometheus_node_job}",'
        f'instance="{deps.settings.prometheus_node_instance}"'
    )
    node_name = deps.settings.prometheus_node_name
    service_metric_labels = (
        f'job="{deps.settings.prometheus_service_job}",'
        f'instance="{deps.settings.prometheus_service_instance}"'
    )
    service_application = deps.settings.prometheus_service_application.strip()
    service_heap_labels = service_metric_labels
    if service_application and service_application.lower() != "none":
        service_heap_labels = f'{service_heap_labels},application="{service_application}"'
    loki_app_names = [
        app.strip()
        for app in (
            f"{deps.settings.loki_container_apps},{deps.settings.loki_system_apps}"
        ).split(",")
        if app.strip()
    ]
    loki_query = build_loki_error_query(deps.settings.loki_app_label, loki_app_names)

    prometheus_queries = {
        "node_up": f"up{{{node_metric_labels}}}",
        "node_cpu_busy_percent": (
            "100 * (1 - avg(rate(node_cpu_seconds_total"
            f'{{mode="idle",{node_metric_labels}}}[5m])))'
        ),
        "node_system_load_percent": (
            "scalar(node_load1"
            f'{{{node_metric_labels},nodename="{node_name}"}}'
            ") * 100 / count(count(node_cpu_seconds_total"
            f"{{{node_metric_labels}}}"
            ") by (cpu))"
        ),
        "node_ram_used_percent": (
            "clamp_min((((node_memory_active_bytes"
            f"{{{node_metric_labels}}}"
            " + node_memory_wired_bytes"
            f"{{{node_metric_labels}}}"
            " + node_memory_compressed_bytes"
            f"{{{node_metric_labels}}}"
            ") / node_memory_total_bytes"
            f"{{{node_metric_labels}}}"
            ") * 100), 0)"
        ),
        "service_up": f"up{{{service_metric_labels}}}",
        "service_process_cpu_usage": f"max_over_time(process_cpu_usage{{{service_metric_labels}}}[5m])",
        "service_jvm_heap_used_percent": (
            "sum(jvm_memory_used_bytes"
            f"{{{service_heap_labels},area=\"heap\"}}"
            ") * 100 / sum(jvm_memory_max_bytes"
            f"{{{service_heap_labels},area=\"heap\"}}"
            ")"
        ),
        "service_http_5xx_rate": (
            "sum(rate(http_server_requests_seconds_count"
            f'{{{service_metric_labels},status=~"5.."}}[5m]))'
        ),
        "service_http_p95_seconds": (
            "histogram_quantile(0.95, "
            "sum by (le, uri) (rate(http_server_requests_seconds_bucket"
            f"{{{service_metric_labels}}}[5m]))"
            ")"
        ),
    }

    metric_names = list(prometheus_queries.keys())
    metric_results = await asyncio.gather(
        *[
            deps.prometheus.query_range(prometheus_queries[name], start, end, "60s")
            for name in metric_names
        ]
    )
    metrics = dict(zip(metric_names, metric_results))

    loki_logs_payload = await deps.loki.query_range(
        query=loki_query,
        start=start,
        end=end,
        limit=500,
    )
    service_logs = flatten_loki_streams(loki_logs_payload, deps.settings.loki_app_label)
    failed_paths = summarize_loki_apps(service_logs)

    summary = await deps.gemini.summarize(
        build_incident_analysis_prompt(deps.settings),
        {
            "timeRangeMinutes": request.minutes,
            "metrics": metrics,
            "lokiQuery": loki_query,
            "serviceLogs": service_logs,
            "logSourceCounts": failed_paths,
        },
    )

    return IncidentResponse(
        time_range_minutes=request.minutes,
        failed_path_count=len(failed_paths),
        error_log_count=len(service_logs),
        summary=summary,
    )
