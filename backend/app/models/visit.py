"""
"""

from datetime import datetime
from dataclasses import dataclass

@dataclass
class Visit:
    id: int
    date: datetime
    diagnosis: str
    prescription: str
    notes: str
    fees_paid: float
    fees_remaining: float

