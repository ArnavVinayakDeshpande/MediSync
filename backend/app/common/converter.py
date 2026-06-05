"""
"""

from datetime import datetime

def date_to_db_fmt(dt: datetime | None) -> str | None:
    return dt.strftime("%m-%d-%Y") if dt else None

def date_from_db_fmt(dt: str | None) -> datetime | None:
    return datetime.strptime(dt, "%m-%d-%Y") if dt else None

