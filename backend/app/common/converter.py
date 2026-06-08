"""
"""

from datetime import datetime, date

def date_to_db_fmt(dt: date | None) -> str | None:
    return dt.strftime("%m-%d-%Y") if dt else None

def date_from_db_fmt(dt: str | None) -> date | None:
    return datetime.strptime(dt, "%m-%d-%Y").date() if dt else None

