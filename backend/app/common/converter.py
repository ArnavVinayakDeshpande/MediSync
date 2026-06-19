"""
"""

from datetime import datetime, date, timedelta, time

from app.models.patient import Patient
from app.models.visit import Visit
from app.models.medical_condition import MedicalCondition
from app.communication.whatsapp.message import (
    WhatsAppMessageType,
    WhatsAppMessageStatus,
    WhatsAppMessage
)
from app.communication.whatsapp.template import (
    WhatsAppTemplateCategory,
    WhatsAppTemplateLanguage,
    WhatsAppTemplateApprovalStatus,
    WhatsAppTemplateStatus,
    WhatsAppTemplate
)


# DB 
def date_to_db_fmt(dt: date | None) -> str | None:
    return dt.strftime("%Y-%m-%d") if dt else None

def date_from_db_fmt(dt: str | None) -> date | None:
    return datetime.strptime(dt, "%Y-%m-%d").date() if dt else None

def datetime_to_db_fmt(dt: datetime | None) -> str | None:
    return dt.strftime("%Y-%m-%d") if dt else None

def datetime_from_db_fmt(dt: str | None) -> datetime | None:
    return datetime.strptime(dt, "%Y-%m-%d") if dt else None

def patient_to_db_fmt(patient: Patient) -> dict:
    return {
        "id": patient.id,
        "name": patient.name,
        "dob": date_to_db_fmt(patient.dob),
        "number": patient.number,
        "condition": patient.condition.value,
        "is_active": patient.is_active
    }

def patient_from_db_fmt(patient: dict) -> Patient:
    return Patient(
        id = patient["id"],
        name = patient["name"],
        dob = date_from_db_fmt(patient["dob"]),
        number = patient["number"],
        condition = MedicalCondition(patient["condition"]),
        is_active = patient["is_active"]
    )

def visit_to_db_fmt(
    patient_id: str,
    visit: Visit
) -> dict:
    return {
        "pid": patient_id,
        "id": visit.id,
        "date": date_to_db_fmt(visit.date),
        "diagnosis": visit.diagnosis,
        "prescription": visit.prescription,
        "notes": visit.notes,
        "fees_paid": visit.fees_paid,
        "fees_pending": visit.fees_pending,
        "follow_up_date": date_to_db_fmt(visit.follow_up_date)
    }

def visit_from_db_fmt(visit: dict) -> tuple[str, Visit]:
    return (
        visit["pid"],
        Visit(
            id = visit["id"],
            date = date_from_db_fmt(visit["date"]),
            diagnosis = visit["diagnosis"],
            prescription = visit["prescription"],
            notes = visit["notes"],
            fees_paid = visit["fees_paid"],
            fees_pending = visit["fees_pending"],
            follow_up_date = date_from_db_fmt(visit["follow_up_date"])
        )
    )

def whatsapp_message_to_db_fmt(message: WhatsAppMessage) -> dict:
    return {
        "id": message.id,
        "whatsapp_id": message.whatsapp_id,
        "msg_type": message.msg_type.value,
        "recipient_number": message.recipient_number,
        "template": {
            "name": message.template_name,
            "id": message.template_id,
            "language": message.language.value if message.language else None
        },
        "text": message.text,
        "sent_on": datetime_to_db_fmt(message.sent_on),
        "delivered_on": datetime_to_db_fmt(message.delivered_on),
        "read_on": datetime_to_db_fmt(message.read_on),
        "created_on": datetime_to_db_fmt(message.created_on),
        "parameters": message.parameters
    } 

def whatsapp_message_from_db_fmt(message: dict) -> WhatsAppMessage:
    return WhatsAppMessage(
        id = message["id"],
        whatsapp_id = message["whatsapp_id"],
        msg_type = WhatsAppMessageType(message["msg_type"]),
        recipient_number = message["recipient_number"],
        template_name = message["template"]["name"],
        template_id = message["template"]["id"],
        text = message["text"],
        language = WhatsAppTemplateLanguage(message["template"]["language"]) if message["template"]["language"] else None,
        sent_on = datetime_from_db_fmt(message["sent_on"]),
        delivered_on = datetime_from_db_fmt(message["delivered_on"]),
        read_on = datetime_from_db_fmt(message["read_on"]),
        created_on = datetime_from_db_fmt(message["created_on"]), # pyright: ignore [reportArgumentType]
        parameters = message["parameters"]
    )

# JSON
def date_to_json_fmt(dt: date | None) -> str | None:
    return dt.strftime("%d-%m-%Y") if dt else None

def date_from_json_fmt(dt: str | None) -> date | None:
    return datetime.strptime(dt, "%d-%m-%Y").date() if dt else None

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

def visit_to_json_fmt(
    visit: Visit,
    patient_id: str,
    patient_name: str) -> dict:
    return {
        "visit": {
            "id": visit.id,
            "date": date_to_json_fmt(visit.date),
            "diagnosis": visit.diagnosis,
            "prescription": visit.prescription,
            "notes": visit.notes,
            "fees_paid": visit.fees_paid,
            "fees_pending": visit.fees_pending,
            "follow_up_date": date_to_json_fmt(visit.follow_up_date)
        },
        "patient": {
            "id": patient_id,
            "name": patient_name
        }
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

# Helper
def age_to_date_range(age: int) -> tuple[date, date]:
    today = date.today()

    youngest = today.replace(year = today.year - age)
    oldest = today.replace(year = youngest.year - 1) + timedelta(days = 1)

    return (youngest, oldest)

def date_to_datetime_range(d: date) -> tuple[datetime, datetime]:
    start = datetime.combine(d, time.min)
    end = start + timedelta(days = 1)

    return (start , end)

def condition_object_to_str(condition: MedicalCondition) -> str:
    return condition.replace("_", " ").title() if condition != MedicalCondition.PCOS else "PCOS" 

def condition_str_to_object(condition: str) -> MedicalCondition:
    return MedicalCondition(condition.replace(" ", "_").upper())

