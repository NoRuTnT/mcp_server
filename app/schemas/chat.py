from datetime import date

from pydantic import BaseModel, Field


class ChatTopicRequest(BaseModel):
    date: date = Field(..., description="YYYY-MM-DD")
    limit: int = Field(default=3000, ge=100, le=10000)


class ChatTopicResponse(BaseModel):
    date: date
    row_count: int
    summary: str
