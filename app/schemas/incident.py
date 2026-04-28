from pydantic import BaseModel, Field


class IncidentRequest(BaseModel):
    minutes: int = Field(default=30, ge=5, le=120)


class IncidentResponse(BaseModel):
    time_range_minutes: int
    failed_path_count: int
    error_log_count: int
    summary: str
