import json
import re
from typing import Any

from app.mcp.deps import AnalysisDependencies


def fallback_route_ops_prompt(prompt: str) -> dict[str, Any]:
    normalized = prompt.lower()
    if any(keyword in normalized for keyword in ["보안", "공격", "스캔", "scan", "nginx", "비정상 접근"]):
        return {"tool": "analyze_security_risks", "arguments": {"days": _extract_days(normalized)}}

    if any(keyword in normalized for keyword in ["장애", "로그", "서버", "메트릭", "에러", "error", "최근"]):
        return {"tool": "analyze_incident", "arguments": {"minutes": _extract_minutes(normalized)}}

    return {
        "tool": "clarify",
        "arguments": {
            "question": "장애 분석 또는 보안 로그 분석 중 어떤 작업을 원하시나요?"
        },
    }


async def route_ops_prompt(prompt: str, deps: AnalysisDependencies) -> dict[str, Any]:
    router_prompt = deps.settings.prompt_ops_router.strip()
    if not router_prompt or not deps.settings.gemini_api_key:
        return fallback_route_ops_prompt(prompt)

    response = await deps.gemini.generate_text(
        f"{router_prompt}\n\n[사용자 요청]\n{prompt}"
    )
    try:
        routed = _parse_json_object(response)
    except ValueError:
        return fallback_route_ops_prompt(prompt)

    tool = routed.get("tool")
    arguments = routed.get("arguments") or {}
    if tool not in {"analyze_incident", "analyze_security_risks", "clarify"}:
        return fallback_route_ops_prompt(prompt)

    if tool == "analyze_incident":
        arguments["minutes"] = _clamp_int(arguments.get("minutes"), 30, 5, 120)
    elif tool == "analyze_security_risks":
        arguments["days"] = _clamp_int(arguments.get("days"), 7, 1, 90)

    return {"tool": tool, "arguments": arguments}


def _parse_json_object(text: str) -> dict[str, Any]:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?", "", cleaned, flags=re.IGNORECASE).strip()
        cleaned = re.sub(r"```$", "", cleaned).strip()

    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start < 0 or end < start:
        raise ValueError("No JSON object found")
    return json.loads(cleaned[start : end + 1])


def _extract_minutes(text: str) -> int:
    hour_match = re.search(r"(\d+)\s*(시간|hour|hours)", text)
    if hour_match:
        return _clamp_int(int(hour_match.group(1)) * 60, 30, 5, 120)

    minute_match = re.search(r"(\d+)\s*(분|minute|minutes|min)", text)
    if minute_match:
        return _clamp_int(int(minute_match.group(1)), 30, 5, 120)

    return 30


def _extract_days(text: str) -> int:
    day_match = re.search(r"(\d+)\s*(일|day|days)", text)
    if day_match:
        return _clamp_int(int(day_match.group(1)), 7, 1, 90)

    if "이번주" in text or "week" in text:
        return 7

    return 7


def _clamp_int(value: Any, default: int, minimum: int, maximum: int) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        parsed = default
    return max(minimum, min(maximum, parsed))
