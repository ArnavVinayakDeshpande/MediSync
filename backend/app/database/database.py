"""
"""

import sqlite3 as sql3
from pathlib import Path

from .exceptions import *
from .patient_repo import PatientRepository
from .visits_repo import VisitRepository 


class Database:
    def __init__(self, filepath: Path) -> None:
        self.filepath = filepath

        self.connection = None
        self.patient_repo = None
        self.visit_repo = None

        try:
            self.connection = sql3.connect(self.filepath)

        except sql3.Error as exc:
            raise DatabaseDisconnectedError() from exc

        else:
            self.patient_repo = PatientRepository(self.connection)
            self.visit_repo = VisitRepository(self.connection)

database: Database | None = None

