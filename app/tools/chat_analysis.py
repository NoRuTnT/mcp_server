from app.mcp.deps import AnalysisDependencies
from app.schemas.chat import ChatTopicRequest, ChatTopicResponse
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
    summary = await deps.gemini.summarize(build_chat_analysis_prompt(deps.settings), rows)
    return ChatTopicResponse(date=request.date, row_count=len(rows), summary=summary)
