from pydantic import BaseModel, Field


class SecurityRiskRequest(BaseModel):
    days: int = Field(default=7, ge=1, le=90)


class SecurityRiskResponse(BaseModel):
    days: int
    failed_login_sources: int
    suspicious_path_count: int
    summary: str
