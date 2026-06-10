"""
"""

from datetime import datetime, date

from app.models.patient import Patient
from app.models.visit import Visit
from app.models.medical_condition import MedicalCondition


def date_to_db_fmt(dt: date | None) -> str | None:
    return dt.strftime("%Y-%m-%d") if dt else None

def date_from_db_fmt(dt: str | None) -> date | None:
    return datetime.strptime(dt, "%Y-%m-%d").date() if dt else None

def date_to_json_fmt(dt: date | None) -> str | None:
    return dt.strftime("%d-%m-%Y") if dt else None

def date_from_json_fmt(dt: str | None) -> date | None:
    return datetime.strptime(dt, "%d-%m-%Y") if dt else None

def condition_object_to_str(condition: MedicalCondition) -> str:
    return condition.replace("_", " ").title() if condition != MedicalCondition.PCOS else "PCOS"

def condition_str_to_object(condition: str) -> MedicalCondition:
    return condition.replace(" ", "_").upper()

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

def visit_to_json_fmt(visit: Visit) -> dict:
    return {
            "id": visit.id,
            "date": date_to_json_fmt(visit.date),
            "diagnosis": visit.diagnosis,
            "prescription": visit.prescription,
            "notes": visits.notes,
            "fees_paid": visit.fees_paid,
            "fees_pending": visit.fees_pending,
            "follow_up_date": date_to_json_fmt(visit.follow_up_date)
            }

def visit_from_json_fmt(data: dict) -> Visit:
    return Visit(
            id = data["id"],
            date = date_from_json_fmt(data["date"]),
            diagnosis = data["diagnosis"],
            prescription = data["prescription"],
            notes = data["notes"],
            fees_paid = data["fees_paid"],
            fees_pending = data["fees_pending"],
            follow_up_date = date_from_json_fmt(data["follow_up_date"])
            )

