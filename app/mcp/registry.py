TOOLS = [
    {
        "name": "analyze_chat_topics",
        "description": "특정 날짜의 디스코드 채팅 로그를 주제 기준으로 요약합니다.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "date": {"type": "string", "description": "YYYY-MM-DD"},
                "limit": {"type": "integer", "minimum": 100, "maximum": 10000},
            },
            "required": ["date"],
        },
    },
    {
        "name": "list_chat_dates",
        "description": "요약 가능한 디스코드 채팅 로그 날짜 목록을 조회합니다.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "minimum": 1, "maximum": 365},
            },
            "required": [],
        },
    },
    {
        "name": "analyze_incident",
        "description": "최근 N분 동안의 메트릭과 에러 로그를 분석합니다.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "minutes": {"type": "integer", "minimum": 5, "maximum": 120},
            },
            "required": [],
        },
    },
    {
        "name": "analyze_security_risks",
        "description": "최근 N일 동안의 보안 로그 집계를 분석합니다.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "days": {"type": "integer", "minimum": 1, "maximum": 90},
            },
            "required": [],
        },
    },
]
