from app.mcp.deps import AnalysisDependencies
from app.schemas.chat import ChatDateItem, ChatDateListRequest, ChatDateListResponse, ChatTopicRequest, ChatTopicResponse
from app.services.prompt_builder import build_chat_analysis_prompt


async def analyze_chat_topics_by_date(
    request: ChatTopicRequest,
    deps: AnalysisDependencies,
) -> ChatTopicResponse:
    sql = f"""
    SELECT
      timestamp,
      eventType,
      userName,
      channelName,
      channelId,
      element AS message
    FROM {deps.settings.chat_log_table}
    WHERE toDate(timestamp) = toDate('{request.date.isoformat()}')
      AND eventType = 'CHAT'
    ORDER BY timestamp ASC
    LIMIT {request.limit}
    """

    rows = await deps.clickhouse.query_select(sql)
    if not rows:
        return ChatTopicResponse(
            date=request.date,
            row_count=0,
            summary=f"{request.date.isoformat()} 날짜의 채팅 로그를 찾지 못했습니다.",
        )

    summary = await deps.gemini.summarize(build_chat_analysis_prompt(deps.settings), rows)
    return ChatTopicResponse(date=request.date, row_count=len(rows), summary=summary)


async def list_chat_dates(
    request: ChatDateListRequest,
    deps: AnalysisDependencies,
) -> ChatDateListResponse:
    sql = f"""
    SELECT
      toDate(timestamp) AS date,
      count(*) AS message_count
    FROM {deps.settings.chat_log_table}
    WHERE eventType = 'CHAT'
    GROUP BY date
    ORDER BY date DESC
    LIMIT {request.limit}
    """

    rows = await deps.clickhouse.query_select(sql)
    return ChatDateListResponse(
        dates=[
            ChatDateItem(date=row["date"], message_count=row["message_count"])
            for row in rows
        ]
    )
