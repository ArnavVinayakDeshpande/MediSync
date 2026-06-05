"""

"""

from dataclasses import dataclass
from datetime import datetime

from .visit import Visit
from .medical_condition import MedicalCondition


@dataclass
class PatientMetadata:
    name: str
    dob: datetime
    number: str
    is_active: bool

@dataclass
class Patient:
    id: int
    metadata: PatientMetadata
    visits: list[Visit]

