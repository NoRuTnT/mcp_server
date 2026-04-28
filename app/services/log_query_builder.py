def build_loki_error_query(label_key: str, app_names: list[str]) -> str:
    escaped_apps = "|".join(app_names)
    return (
        f'{{{label_key}=~"{escaped_apps}"}} '
        '|~ "(?i)(error|warn|fail|failed|exception|panic|fatal|crit|emerg|alert|502|503|504)"'
    )
