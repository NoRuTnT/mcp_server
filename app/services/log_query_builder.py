def build_loki_error_query(label_key: str, app_names: list[str]) -> str:
    escaped_apps = "|".join(app_names)
    return (
        f'{{{label_key}=~"{escaped_apps}"}} '
        '|~ "(?i)(error|warn|fail|failed|exception|panic|fatal|crit|emerg|alert|502|503|504)"'
    )


def build_loki_security_query(label_key: str, app_names: list[str]) -> str:
    escaped_apps = "|".join(app_names)
    return (
        f'{{{label_key}=~"{escaped_apps}"}} '
        '|~ "(?i)(wp-admin|phpmyadmin|\\\\.env|/admin|\\\\.git|\\\\.sql|passwd|\\\\.DS_Store|\\.\\./|%2e%2e|union select|select.+from|<script|curl|wget|nmap|masscan|401|403|429|500|502|503|504)"'
    )
