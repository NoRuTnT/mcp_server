# MCP Client Integration Guide

이 문서는 다른 프로젝트가 `mcp_server`를 호출하는 방법을 설명한다.
대상 클라이언트는 Discord bot, 내부 관리자 웹, 프론트엔드 운영 페이지 등이다.

이 문서에는 실제 토큰, 내부 URL, 운영 라벨 값, 데이터베이스 인증 정보를 적지 않는다.
환경별 값은 각 클라이언트 프로젝트의 `.env` 또는 배포 설정에서 관리한다.

## 기본 개념

MCP 서버는 HTTP POST `/mcp` 엔드포인트를 통해 JSON-RPC 형식의 요청을 받는다.

클라이언트는 다음 흐름으로 사용한다.

1. 필요한 기능을 tool 이름으로 선택한다.
2. tool arguments를 만든다.
3. `/mcp`로 `tools/call` 요청을 보낸다.
4. 응답의 `result.content[0].text`를 사용자에게 보여준다.

## MCP Endpoint

같은 Docker network 안에서 호출하는 경우:

```text
http://mcp-server:8000/mcp
```

외부 공개 URL을 사용할 경우에는 API gateway, reverse proxy, 인증 계층을 거친 내부 전용 주소를 사용한다.
운영/보안 로그 분석 기능은 공개 인터넷에 직접 노출하지 않는다.

## Request Format

모든 tool 실행 요청은 아래 형식을 따른다.

```json
{
  "jsonrpc": "2.0",
  "id": "client-request-id",
  "method": "tools/call",
  "params": {
    "name": "tool_name",
    "arguments": {}
  }
}
```

## Response Format

정상 응답:

```json
{
  "jsonrpc": "2.0",
  "id": "client-request-id",
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{...}"
      }
    ]
  },
  "error": null
}
```

클라이언트는 보통 아래 값을 꺼내 사용자에게 보여준다.

```text
result.content[0].text
```

오류 응답:

```json
{
  "jsonrpc": "2.0",
  "id": "client-request-id",
  "result": null,
  "error": {
    "code": -32602,
    "message": "error message"
  }
}
```

사용자에게는 일반적인 실패 메시지를 보여주고, `error.message`는 관리자 로그에만 남기는 것을 권장한다.

## Available Tools

### `list_chat_dates`

요약 가능한 Discord 채팅 날짜 목록을 조회한다.

사용 예:

```json
{
  "jsonrpc": "2.0",
  "id": "chat-date-list",
  "method": "tools/call",
  "params": {
    "name": "list_chat_dates",
    "arguments": {
      "limit": 10
    }
  }
}
```

응답 예:

```json
{
  "dates": [
    {
      "date": "2026-06-09",
      "message_count": 18
    }
  ]
}
```

권장 UI:

- Discord: `/채팅날짜`
- Web: 날짜 선택 드롭다운 또는 최근 날짜 목록

### `analyze_chat_topics`

특정 날짜의 Discord 채팅 로그를 요약한다.

사용 예:

```json
{
  "jsonrpc": "2.0",
  "id": "chat-summary",
  "method": "tools/call",
  "params": {
    "name": "analyze_chat_topics",
    "arguments": {
      "date": "2026-04-27",
      "limit": 3000
    }
  }
}
```

응답 예:

```json
{
  "date": "2026-04-27",
  "row_count": 63,
  "summary": "주요 주제..."
}
```

로그가 없는 날짜의 응답 예:

```json
{
  "date": "1999-01-01",
  "row_count": 0,
  "summary": "1999-01-01 날짜의 채팅 로그를 찾지 못했습니다."
}
```

권장 UI:

- Discord: `/채팅요약 date`
- Web: 날짜 선택 후 요약 버튼

### `analyze_incident`

최근 N분 동안의 서버 메트릭, 서비스 메트릭, Loki 운영 로그를 분석한다.

사용 예:

```json
{
  "jsonrpc": "2.0",
  "id": "incident-analysis",
  "method": "tools/call",
  "params": {
    "name": "analyze_incident",
    "arguments": {
      "minutes": 30
    }
  }
}
```

권장 UI:

- Discord 일반 채널에는 노출하지 않는다.
- Web 관리자 페이지에서만 사용한다.
- 기간 선택은 `5분`, `15분`, `30분`, `60분`, `120분` 같은 preset을 권장한다.

### `analyze_ops_prompt`

운영/보안 관련 자연어 요청을 MCP 서버 내부에서 해석하고, 적절한 분석 tool을 실행한다.
프론트엔드에서 Gemini API key를 직접 사용하지 않기 위한 관리자 웹 전용 진입점이다.

사용 예:

```json
{
  "jsonrpc": "2.0",
  "id": "ops-prompt-analysis",
  "method": "tools/call",
  "params": {
    "name": "analyze_ops_prompt",
    "arguments": {
      "prompt": "최근 30분 서버 상태랑 에러 로그를 분석해줘"
    }
  }
}
```

응답 예:

```json
{
  "prompt": "최근 30분 서버 상태랑 에러 로그를 분석해줘",
  "selected_tool": "analyze_incident",
  "arguments": {
    "minutes": 30
  },
  "result": {
    "time_range_minutes": 30,
    "failed_path_count": 0,
    "error_log_count": 0,
    "summary": "..."
  },
  "summary": "..."
}
```

권장 UI:

- Web 관리자 페이지에서만 사용한다.
- 브라우저는 Gemini를 직접 호출하지 않는다.
- 브라우저는 관리자 백엔드 또는 BFF로 자연어 요청을 보내고, 서버 쪽에서 MCP 서버를 호출한다.

### `analyze_security_risks`

최근 N일 동안 Loki 보안 관련 로그를 분석한다.

사용 예:

```json
{
  "jsonrpc": "2.0",
  "id": "security-analysis",
  "method": "tools/call",
  "params": {
    "name": "analyze_security_risks",
    "arguments": {
      "days": 7
    }
  }
}
```

권장 UI:

- Discord 일반 채널에는 노출하지 않는다.
- Web 관리자 페이지에서만 사용한다.
- 기간 선택은 `1일`, `3일`, `7일`, `30일` 같은 preset을 권장한다.

## Tool Exposure Policy

클라이언트별로 노출할 tool을 분리한다.

Discord bot 권장 노출:

- `list_chat_dates`
- `analyze_chat_topics`

관리자 웹 권장 노출:

- `list_chat_dates`
- `analyze_chat_topics`
- `analyze_ops_prompt`
- `analyze_incident`
- `analyze_security_risks`

운영/보안 tool은 내부 정보가 포함될 수 있으므로 일반 Discord 채널에 노출하지 않는다.

## Frontend Integration Pattern

프론트엔드 웹은 브라우저에서 MCP 서버를 직접 호출하지 않는 것을 권장한다.
대신 프론트엔드 백엔드 또는 BFF가 MCP 서버를 호출하고, 브라우저에는 정제된 결과만 반환한다.

권장 흐름:

```text
Browser
-> Frontend Backend / BFF
-> MCP Server
-> Prometheus / Loki / ClickHouse / Gemini
-> Frontend Backend / BFF
-> Browser
```

이유:

- MCP 서버 URL과 내부 네트워크 구조를 브라우저에 노출하지 않는다.
- 운영/보안 분석 tool에 대한 권한 제어를 서버에서 처리할 수 있다.
- Gemini API key를 브라우저에 노출하지 않는다.
- 응답을 웹 UI에 맞게 가공할 수 있다.

## Discord Integration Pattern

Discord bot은 slash command로 의도를 먼저 나누는 방식을 권장한다.

권장 slash command:

```text
/채팅날짜 limit
/채팅요약 date
```

운영/보안 분석은 일반 Discord bot command로 제공하지 않는다.
필요한 경우 관리자 전용 채널과 role check를 반드시 적용한다.

## Message Length Handling

Discord 일반 메시지는 길이 제한이 있으므로 응답이 길면 분할 전송한다.

권장 처리:

```text
if len(text) <= 1900:
  send(text)
else:
  split text into chunks under 1900 chars
```

웹 UI는 긴 응답을 그대로 보여주기보다 섹션 단위로 접거나, 요약과 원본 근거를 분리해 보여주는 것을 권장한다.

## Error Handling

클라이언트는 다음 케이스를 처리한다.

- MCP `error`가 있는 경우
- `result.content`가 비어 있는 경우
- 외부 데이터 소스 연결 실패
- LLM 일시 장애
- 사용자가 날짜나 기간을 잘못 입력한 경우

사용자에게는 짧게 안내한다.

```text
요청을 처리하지 못했습니다. 잠시 후 다시 시도해주세요.
```

관리자 로그에는 MCP `error.message`와 request id를 남긴다.

## Security Notes

- MCP 서버를 공개 인터넷에 직접 노출하지 않는다.
- 운영/보안 tool은 관리자 권한이 있는 클라이언트에서만 호출한다.
- API key, DB credential, 내부 URL, 프롬프트는 저장소에 커밋하지 않는다.
- 브라우저 클라이언트에서 Gemini API key나 MCP 내부 주소를 직접 사용하지 않는다.
- 로그 원문에는 IP, 경로, 계정명, 내부 URL이 포함될 수 있으므로 UI 출력 전에 마스킹 정책을 고려한다.
