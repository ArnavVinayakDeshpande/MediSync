"""
"""

from .visit import Visit
from .medical_condition import MedicalCondition
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Patient:
    id: int
    name: str
    dob: datetime
    number: str
    is_active: bool
    last_visit_date: datetime
    total_fees_paid: float
    fees_remaining: float
    visits: list[Visit]
    condition: MedicalCondition

