"""

"""

from dataclasses import dataclass
from datetime import date

from .visit import Visit
from .medical_condition import MedicalCondition
from app.common.converter import date_to_json_fmt, date_from_json_fmt


@dataclass
class PatientMetadata:
    name: str
    dob: _date 
    number: str
    condition: MedicalCondition
    is_active: bool

@dataclass
class Patient:
    id: int
    metadata: PatientMetadata
    visits: list[Visit]

