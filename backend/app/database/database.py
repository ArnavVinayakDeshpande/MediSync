"""
"""

import sqlite3 as sql3
from pathlib import Path

from app.database.exceptions import *
from app.database.patient_repo import PatientRepository
from app.database.visit_repo import VisitRepository 
from app.database.wa_msg_history_repo import WhatsAppMsgHistoryRepository
from app.database.wa_template_repo import WhatsAppTemplateRepository


class Database:
    def __init__(self, filepath: Path) -> None:
        self.filepath = filepath

        self._connection = None
        self._patient_repo = None
        self._visit_repo = None
        self._wa_msg_history_repo = None
        self._wa_template_repo = None

        try:
            self._connection = sql3.connect(
                self.filepath,
                check_same_thread = False
            )
            self._connection.execute(
                """
                    PRAGMA foreign_keys = ON
                """
            )

        except sql3.Error as exc:
            raise DatabaseDisconnectedError(exc) from exc

        else:
            try:
                self._patient_repo = PatientRepository(self._connection)
                self._visit_repo = VisitRepository(self._connection)
                self._wa_msg_history_repo = WhatsAppMsgHistoryRepository(self._connection)
                self._wa_template_repo = WhatsAppTemplateRepository(self._connection)

            except sql3.Error as exc:
                self._connection.close()
                raise DatabaseDisconnectedError(exc) from exc

    @property
    def patient_repo(self) -> PatientRepository:
        if not self._patient_repo:
            raise DatabaseDisconnectedError()

        return self._patient_repo

    @property
    def visit_repo(self) -> VisitRepository:
        if not self._visit_repo:
            raise DatabaseDisconnectedError()

        return self._visit_repo

    @property
    def wa_msg_history_repo(self) -> WhatsAppMsgHistoryRepository:
        if not self._wa_msg_history_repo:
            raise DatabaseDisconnectedError()

        return self._wa_msg_history_repo

    @property
    def wa_template_repo(self) -> WhatsAppTemplateRepository:
        if not self._wa_template_repo:
            raise DatabaseDisconnectedError()

        return self._wa_template_repo

database: Database | None = None

