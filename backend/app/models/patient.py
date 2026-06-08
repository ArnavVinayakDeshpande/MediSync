"""

"""

from dataclasses import dataclass
from datetime import date

from .visit import Visit
from .medical_condition import MedicalCondition


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

