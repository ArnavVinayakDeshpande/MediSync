"""
"""

from datetime import date

from app.common.id_creater import generate_id
from app.database.database import Database
from app.database.visit_repo import VisitRepository
from .exceptions import *


class VisitManager:
    def __init__(self, database: Database):
        self.database = database

        self._repo = self.database.visit_repo

        if self._repo is None:
            raise VMDatabaseError()

        self._last_id = self._get_last_id()

    def _get_last_id(self):
        pass

    def _rollback_id(self):
        pass

    def _validate(self):
        if self._repo is None:
            raise PMDatabaseError()

    def _validate_inputs(self):
        pass

    def _create_visit(self):
        pass

    def create(self):
        pass

    def delete(self, visit_id: int):
        self._validate()

        try:
            self._repo.delete(visit_id)

        except (DatabaseCursorError, DatabaseExecutionError) as exc:
            raise PMDatabaseError() from exc

        except DatabaseAbsentEntryError:
            raise PMAbsentEntryError()

        else:
            self._repo.commit()

    def deleteall(self, patient_id: int):
        self._validate()

        try:
            self._repo.deletall(patient_id)

        except (DatabaseCursorError, DatabaseExecutionError) as exc:
            raise PMDatabaseError() from exc

        else:
            slef._repo.commit()

    def clear(self):
        self._validate()

        try:
            self._repo.clear()

        except (DatabaseCursorError, DatabaseExecutionError) as exc:
            raise PMDatabaseError() from exc

        else:
            self._repo.commit()

    def get(self, visit_id: int) -> Visit | None:
        self._validate()

        try:
            return self._repo.get(visit_id)

        except (DatabaseCursorError, DatabaseExecutionError) as exc:
            raise PMDatabaseError() from exc


    def getall(self):
        self._validate()

        try:
            return self._repo.getall()

        except (DatabaseCursorError, DatabaseExecutionError) as exc:
            raise PMDatabaseError() from exc

    def update(self):
        pass

visit_manager: VisitManager | None = None

