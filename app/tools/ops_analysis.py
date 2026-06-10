import json

from app.mcp.deps import AnalysisDependencies
from app.schemas.incident import IncidentRequest
from app.schemas.ops import OpsPromptRequest, OpsPromptResponse
from app.schemas.security import SecurityRiskRequest
from app.services.ops_prompt_router import route_ops_prompt
from app.tools.incident_analysis import analyze_incident_last_minutes
from app.tools.security_analysis import analyze_security_risks


async def analyze_ops_prompt(
    request: OpsPromptRequest,
    deps: AnalysisDependencies,
) -> OpsPromptResponse:
    routed = await route_ops_prompt(request.prompt, deps)
    selected_tool = routed["tool"]
    arguments = routed.get("arguments") or {}

    if selected_tool == "analyze_incident":
        result = await analyze_incident_last_minutes(IncidentRequest.model_validate(arguments), deps)
        payload = json.loads(result.model_dump_json())
        return OpsPromptResponse(
            prompt=request.prompt,
            selected_tool=selected_tool,
            arguments=arguments,
            result=payload,
            summary=payload.get("summary"),
        )

    if selected_tool == "analyze_security_risks":
        result = await analyze_security_risks(SecurityRiskRequest.model_validate(arguments), deps)
        payload = json.loads(result.model_dump_json())
        return OpsPromptResponse(
            prompt=request.prompt,
            selected_tool=selected_tool,
            arguments=arguments,
            result=payload,
            summary=payload.get("summary"),
        )

    question = arguments.get("question", "요청을 조금 더 구체적으로 입력해주세요.")
    return OpsPromptResponse(
        prompt=request.prompt,
        selected_tool="clarify",
        arguments={"question": question},
        summary=question,
    )
