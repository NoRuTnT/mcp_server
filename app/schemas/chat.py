from datetime import date as DateType

from pydantic import BaseModel, Field


class ChatTopicRequest(BaseModel):
    date: DateType = Field(..., description="YYYY-MM-DD")
    limit: int = Field(default=3000, ge=100, le=10000)


class ChatTopicResponse(BaseModel):
    date: DateType
    row_count: int
    summary: str


class ChatDateListRequest(BaseModel):
    limit: int = Field(default=30, ge=1, le=365)


class ChatDateItem(BaseModel):
    date: DateType
    message_count: int


class ChatDateListResponse(BaseModel):
    dates: list[ChatDateItem]
