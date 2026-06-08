"""
"""

import sqlite3 as sql3
from pathlib import Path

from .exceptions import *
from .patient_repo import PatientRepository
from .patient_visits_repo import PatientVisitsRepo


class Database:
    def __init__(self, filepath: Path) -> None:
        self.filepath = filepath

        self.connection = None
        self.patient_repo = None
        self.patient_visits_repo = None

        try:
            self.connection = sql3.connect(self.filepath)

        except sql3.Error as exc:
            raise DatabaseDisconnectedError() from exc

        else:
            self.patient_repo = PatientMetadataRepo(self.connection)
            self.patient_visits_repo = PatientVisitsRepo(self.connection)

database: Database | None = None

