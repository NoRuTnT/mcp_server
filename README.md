# mcp_server

디스코드 로그와 운영 지표를 분석하기 위한 MCP 서버 프로젝트입니다.

현재 서버는 `/mcp` 진입점을 기준으로 동작하며, 채팅 로그 요약과 운영 상태 분석을 위한 도구를 제공합니다.

## 현재 구조

```text
mcp_server/
|- app/
|  |- clients/
|  |  |- clickhouse.py
|  |  |- gemini_client.py
|  |  |- loki.py
|  |  |- mysql.py
|  |  `- prometheus.py
|  |- core/
|  |  |- exceptions.py
|  |  `- logging.py
|  |- mcp/
|  |  |- deps.py
|  |  |- registry.py
|  |  |- router.py
|  |  `- schemas.py
|  |- schemas/
|  |  |- chat.py
|  |  |- common.py
|  |  |- incident.py
|  |  `- security.py
|  |- services/
|  |  |- log_formatter.py
|  |  |- log_query_builder.py
|  |  |- prompt_builder.py
|  |  |- response_formatter.py
|  |  `- time_range.py
|  |- tools/
|  |  |- chat_analysis.py
|  |  |- incident_analysis.py
|  |  `- security_analysis.py
|  |- config.py
|  `- main.py
|- .dockerignore
|- Dockerfile
|- main.py
`- requirements.txt
```

## 제공 기능

- 특정 날짜의 Discord 채팅 로그 요약
- 서버 메트릭과 서비스 메트릭 기반 장애 분석
- Loki 로그 기반 운영 로그 요약
- MCP `tools/list`, `tools/call` 처리

## 데이터 소스

- ClickHouse: 채팅 이벤트 및 저장 로그 조회
- Prometheus: `job` 라벨 기준 메트릭 조회
- Loki: `job` 라벨 기준 로그 조회
- Gemini: 분석 결과 요약

## 설정

실행에 필요한 값은 `.env`로 주입합니다.

- 데이터 저장소 주소 및 인증 정보
- Prometheus / Loki 조회 대상 라벨 값
- Gemini API 키
- 분석 프롬프트

## 배포

프로젝트 루트의 `Dockerfile` 기준으로 컨테이너 이미지를 빌드해 배포할 수 있습니다.
