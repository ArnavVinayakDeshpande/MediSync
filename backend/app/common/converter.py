"""
"""

from datetime import datetime, date

from app.models.patient import Patient
from app.models.visit import Visit


def date_to_db_fmt(dt: date | None) -> str | None:
    return dt.strftime("%m-%d-%Y") if dt else None

def date_from_db_fmt(dt: str | None) -> date | None:
    return datetime.strptime(dt, "%m-%d-%Y").date() if dt else None

def date_to_json_fmt(dt: date | None) -> str | None:
    return dt.strftime("%d-%m-%Y") if dt else None

def date_from_json_fmt(dt: str | None) -> date | None:
    return datetime.strptime("%d-%m-%Y") if dt else None

def condition_object_to_str(condition: MedicalCondition) -> str:
    return condition.replace("_", " ").title()

def condition_str_to_object(mc_text: str) -> MedicalCondition:
    return mc.replace(" ", "_").upper()

def patient_to_json_fmt(patient: Patient) -> dict:
    return {
            "id": patient.id,
            "name": patient.name,
            "dob": date_to_json_fmt(patient.dob),
            "number": patient.number,
            "condition": condition_object_to_str(patient.condition),
            "is_active": patient.is_active
            }

def patient_from_json_fmt(data: dict) -> Patient:
    return Patient(
            id = data["id"],
            name = data["name"],
            dob = date_from_json_fmt(data["dob"]),
            number = data["number"],
            condition = condition_str_to_object(data["condition"]),
            is_active = data["is_active"]
            )

