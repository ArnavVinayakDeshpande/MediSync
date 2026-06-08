"""
"""

from datetime import datetime, date

from app.models.patient import *
from app.models.visit import *


def date_to_db_fmt(dt: date | None) -> str | None:
    return dt.strftime("%m-%d-%Y") if dt else None

def date_from_db_fmt(dt: str | None) -> date | None:
    return datetime.strptime(dt, "%m-%d-%Y").date() if dt else None

def date_to_json_fmt(dt: date | None) -> str | None:
    return dt.strftime("%d-%m-%Y") if dt else None

def date_from_json_fmt(dt: str | None) -> date | None:
    return datetime.strptime("%d-%m-%Y") if dt else None

def patient_metadata_to_json_fmt(pid: int, pmd: PatientMetadata) -> dict:
    return {
            "id": pid,
            "name": pmd.name,
            "dob": date_to_json_fmt(pmd.dob),
            "number": pmd.number,
            "condition": pmd.condition,
            "is_active": pmd.is_active
            }

