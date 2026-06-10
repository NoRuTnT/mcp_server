from typing import Any, Literal

from pydantic import BaseModel, Field


class OpsPromptRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=4000)


class OpsPromptResponse(BaseModel):
    prompt: str
    selected_tool: Literal["analyze_incident", "analyze_security_risks", "clarify"]
    arguments: dict[str, Any]
    result: dict[str, Any] | None = None
    summary: str | None = None
