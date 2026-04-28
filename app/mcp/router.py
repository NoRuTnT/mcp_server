import json

from fastapi import APIRouter, Depends

from app.mcp.deps import AnalysisDependencies, get_analysis_dependencies
from app.mcp.registry import TOOLS
from app.mcp.schemas import MCPRequest, MCPResponse
from app.schemas.chat import ChatTopicRequest
from app.schemas.incident import IncidentRequest
from app.schemas.security import SecurityRiskRequest
from app.services.response_formatter import format_mcp_text_result
from app.tools.chat_analysis import analyze_chat_topics_by_date
from app.tools.incident_analysis import analyze_incident_last_minutes
from app.tools.security_analysis import analyze_security_risks

router = APIRouter(prefix="/mcp", tags=["mcp"])


@router.post("", response_model=MCPResponse)
async def mcp_rpc(
    request: MCPRequest,
    deps: AnalysisDependencies = Depends(get_analysis_dependencies),
) -> MCPResponse:
    if request.method == "tools/list":
        return MCPResponse(id=request.id, result={"tools": TOOLS})

    if request.method != "tools/call":
        return MCPResponse(id=request.id, error={"code": -32601, "message": "Method not found"})

    name = request.params.get("name")
    arguments = request.params.get("arguments", {})

    try:
        if name == "analyze_chat_topics":
            result = await analyze_chat_topics_by_date(ChatTopicRequest.model_validate(arguments), deps)
        elif name == "analyze_incident":
            result = await analyze_incident_last_minutes(IncidentRequest.model_validate(arguments), deps)
        elif name == "analyze_security_risks":
            result = await analyze_security_risks(SecurityRiskRequest.model_validate(arguments), deps)
        else:
            return MCPResponse(id=request.id, error={"code": -32601, "message": "Unknown tool"})
    except Exception as exc:
        return MCPResponse(id=request.id, error={"code": -32602, "message": str(exc)})

    return MCPResponse(id=request.id, result=format_mcp_text_result(json.loads(result.model_dump_json())))
