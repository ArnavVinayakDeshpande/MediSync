"""

"""

from dataclasses import dataclass
from datetime import date

from .visit import Visit
from .medical_condition import MedicalCondition


@dataclass
class Patient:
    id: str
    name: str
    dob: date | None
    number: str
    condition: MedicalCondition
    is_active: bool

