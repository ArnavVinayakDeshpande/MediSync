"""
"""

from datetime import date as _date
from dataclasses import dataclass


@dataclass
class Visit:
    id: int
    date: _date | None
    diagnosis: str
    prescription: str
    notes: str
    fees_paid: float
    fees_pending: float
    follow_up_date: _date | None

