from collections import Counter
from typing import Any


def flatten_loki_streams(payload: dict[str, Any], app_label_key: str) -> list[dict[str, Any]]:
    streams = payload.get("data", {}).get("result", [])
    rows: list[dict[str, Any]] = []
    for stream in streams:
        labels = stream.get("stream", {})
        for ts, line in stream.get("values", []):
            rows.append(
                {
                    "timestamp_ns": ts,
                    "app": (
                        labels.get(app_label_key)
                        or labels.get("service")
                        or labels.get("job")
                        or labels.get("app")
                        or "unknown"
                    ),
                    "labels": labels,
                    "message": line,
                }
            )
    return rows


def summarize_loki_apps(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    counts = Counter(row["app"] for row in rows)
    return [{"app": app, "count": count} for app, count in counts.most_common()]
