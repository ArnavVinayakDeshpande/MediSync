"""
"""

from datetime import date as _date

from app.common.id_creater import generate_id
from app.database.database import Database
from app.database.exceptions import *
from app.managers.exceptions import *
from app.database.visit_repo import VisitRepository
from app.models.visit import Visit


class VisitManager:
    def __init__(self, database: Database):
        self.database = database

        self._repo = self.database.visit_repo

        if self._repo is None:
            raise VMDatabaseError(DatabaseCursorError())

        self._reserved_ids: list[str] = []

        self._id_len = 8

    def _validate(self):
        if self._repo is None:
            raise VMDatabaseError(DatabaseCursorError())

    def _validate_inputs(
            self,
            id: str | None,
            date: _date | None,
            fees_paid: float,
            fees_pending: float,
            follow_up_date: _date | None):
        if id is not None:
            if not id:
                raise VMInvalidInputsError()

            if len(id) != self._id_len:
                raise VMInvalidInputsError()

            if id != id.upper():
                raise VMInvalidInputsError()

        todays_date = _date.today()

        if date is not None:
            if date > todays_date:
                raise VMInvalidInputsError()

        if fees_paid < 0:
            raise VMInvalidInputsError()

        if fees_pending < 0:
            raise VMInvalidInputsError()

        if follow_up_date is not None:
            if follow_up_date < todays_date:
                raise VMInvalidInputsError()

    def create(
            self,
            patient_id: str,
            visit: Visit) -> str:
        self._validate()

        try:
            self._validate_inputs(
                    id = visit.id,
                    date = visit.date,
                    fees_paid = visit.fees_paid,
                    fees_pending = visit.fees_pending,
                    follow_up_date = visit.follow_up_date
                    )

            if visit.id in self._reserved_ids:
                self._reserved_ids.remove(visit.id)

            self._repo.insert(patient_id, visit)

        except (DatabaseCursorError, DatabaseExecutionError) as exc:
            raise VMDatabaseError(exc) from exc

        except DatabaseDuplicateEntryError as exc:
            raise VMDuplicateEntryError() from exc

        else:
            self._repo.commit()
            return visit.id

    def delete(self, visit_id: str):
        self._validate()

        try:
            self._repo.delete(visit_id)

        except (DatabaseCursorError, DatabaseExecutionError) as exc:
            raise VMDatabaseError(exc) from exc

        except DatabaseAbsentEntryError as exc:
            raise VMAbsentEntryError() from exc

        else:
            self._repo.commit()

    def deleteall(self, patient_id: str):
        self._validate()

        try:
            self._repo.deleteall(patient_id)

        except (DatabaseCursorError, DatabaseExecutionError) as exc:
            raise VMDatabaseError(exc) from exc

        else:
            self._repo.commit()

    def clear(self):
        self._validate()

        try:
            self._repo.clear()

        except (DatabaseCursorError, DatabaseExecutionError) as exc:
            raise VMDatabaseError(exc) from exc

        else:
            self._repo.commit()

    def get(self, visit_id: str) -> Visit | None:
        self._validate()

        try:
            return self._repo.get(visit_id)

        except (DatabaseCursorError, DatabaseExecutionError) as exc:
           raise VMDatabaseError(exc) from exc

    def getall(
            self,
            patient_id: str | None = None,
            size: int | None = None,
            offset: int | None = None,
            fees_pending: bool | None = None,
            follow_up: bool | None = None) -> list[Visit]:
        self._validate()

        try:
            return self._repo.getall(
                    patient_id = patient_id,
                    size = size,
                    offset = offset,
                    fees_pending = fees_pending,
                    follow_up = follow_up
                    )

        except (DatabaseCursorError, DatabaseExecutionError) as exc:
            raise VMDatabaseError(exc) from exc

    def update(
            self,
            visit_id: str,
            date: _date | None = None,
            diagnosis: str | None = None,
            prescription: str | None = None,
            notes: str | None = None,
            fees_paid: float | None = None,
            fees_pending: float | None = None,
            follow_up_date: _date | None = None
            ):
        self._validate()

        try:
            self._validate_inputs(
                    id = visit_id,
                    date = date,
                    fees_paid = fees_paid if fees_paid is not None else 0,
                    fees_pending = fees_pending if fees_pending is not None else 0,
                    follow_up_date = follow_up_date
                    )

            visit = self.get(visit_id)

            if visit is None:
                raise VMAbsentEntryError()

            visit.date = date if date else visit.date
            visit.diagnosis = diagnosis if diagnosis is not None else visit.diagnosis
            visit.prescription = prescription if prescription is not None else visit.prescription
            visit.notes = notes if notes is not None else visit.notes
            visit.fees_paid = fees_paid if fees_paid is not None else visit.fees_paid
            visit.fees_pending = fees_pending if fees_pending is not None else visit.fees_pending
            visit.follow_up_date = follow_up_date if follow_up_date else visit.follow_up_date

            self._repo.update(visit)

        except (DatabaseCursorError, DatabaseExecutionError) as exc:
            raise VMDatabaseError(exc) from exc

        except DatabaseAbsentEntryError as exc:
            raise VMAbsentEntryError() from exc

    def exists(self, visit_id: str) -> bool:
        self._validate()

        try:
            return self._repo.exists(visit_id)

        except (DatabaseCursorError, DatabaseExecutionError) as exc:
            raise VMDatabaseError(exc) from exc

    def create_id(self) -> str:
        visit_id = generate_id(length = self._id_len)

        self._reserved_ids.append(visit_id)

        return visit_id

visit_manager: VisitManager | None = None

