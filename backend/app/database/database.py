"""
"""

import sqlite3 as sql3
from pathlib import Path

from app.database.exceptions import *
from app.database.patient_repo import PatientRepository
from app.database.visit_repo import VisitRepository 
from app.database.wa_msg_history_repo import WhatsAppMsgHistoryRepository


class Database:
    def __init__(self, filepath: Path) -> None:
        self.filepath = filepath

        self.connection = None
        self.patient_repo = None
        self.visit_repo = None
        self.wa_msg_history_repo = None

        try:
            self.connection = sql3.connect(
                    self.filepath,
                    check_same_thread = False
                    )
            self.connection.execute(
                    """
                    PRAGMA foreign_keys = ON
                    """
                    )

        except sql3.Error as exc:
            raise DatabaseDisconnectedError(exc) from exc

        else:
            try:
                self.patient_repo = PatientRepository(self.connection)
                self.visit_repo = VisitRepository(self.connection)
                self.wa_msg_history_repo = WhatsAppMsgHistoryRepository(self.connection)

            except sql3.Error as exc:
                self.connection.close()
                raise DatabaseDisconnectedError(exc) from exc

database: Database | None = None

