from datetime import datetime, timedelta, timezone


def recent_utc_window(minutes: int) -> tuple[datetime, datetime]:
    end = datetime.now(timezone.utc)
    start = end - timedelta(minutes=minutes)
    return start, end
