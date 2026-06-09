"""

"""

from dataclasses import dataclass
from datetime import date

from .visit import Visit
from .medical_condition import MedicalCondition
from app.common.converter import date_to_json_fmt, date_from_json_fmt


@dataclass
class Patient:
    id: str
    name: str
    dob: _date | None
    number: str
    condition: MedicalCondition
    is_active: bool

