"""
"""

from datetime import date as _date
from dataclasses import dataclass

from app.common.id_creater import generate_id
from app.database.database import Database
from app.database.exceptions import *
from app.managers.exceptions import *
from app.database.visit_repo import VisitRepository, VisitRepositoryGetResult
from app.models.visit import Visit


@dataclass
class VisitManagerGetResult:
    visit: Visit
    patient_id: str

@dataclass
class VisitManagerGetFieldsResult:
    id: str
    patient_id: str | None = None
    date: _date | None = None
    diagnosis: str | None = None
    prescription: str | None = None
    notes: str | None = None
    fees_paid: float | None = None
    fees_pending: float | None = None
    follow_up_date: _date | None = None

class VisitManager:
    def __init__(self, database: Database):
        self.database = database

        try:
            self._repo: VisitRepository = self.database.visit_repository

        except DatabaseDisconnectedError as exc:
            raise VMDatabaseError(exc) from exc

        self._reserved_ids: list[str] = []
        self._id_len = 8

    def _validate_inputs(
        self,
        id: str | None,
        date: _date | None,
        fees_paid: float,
        fees_pending: float,
        follow_up_date: _date | None
    ):
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

    def _to_vm_get_result(self, result: VisitRepositoryGetResult) -> VisitManagerGetResult:
        return VisitManagerGetResult(
            visit = result.visit,
            patient_id = result.patient_id 
        )

    def create(
        self,
        patient_id: str,
        visit: Visit
    ) -> str:
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
            return visit.id

    def delete(self, visit_id: str):
        try:
            self._repo.delete(visit_id)

        except (DatabaseCursorError, DatabaseExecutionError) as exc:
            raise VMDatabaseError(exc) from exc

        except DatabaseAbsentEntryError as exc:
            raise VMAbsentEntryError() from exc

    def deleteall(self, patient_id: str):
        try:
            self._repo.deleteall(patient_id)

        except (DatabaseCursorError, DatabaseExecutionError) as exc:
            raise VMDatabaseError(exc) from exc

    def get(self, visit_id: str) -> VisitManagerGetResult | None:
        try:
            data = self._repo.get(visit_id)

            return self._to_vm_get_result(data) if data is not None else None

        except (DatabaseCursorError, DatabaseExecutionError) as exc:
           raise VMDatabaseError(exc) from exc

    def getall(
        self,
        patient_id: str | None = None,
        size: int = 0,
        offset: int = 0,
        fees_pending: bool | None = None,
        follow_up: bool | None = None
    ) -> list[VisitManagerGetResult]:
        try:
            return [
                self._to_vm_get_result(visit) for visit in (
                    self._repo.getall(
                        patient_id = patient_id,
                        size = size,
                        offset = offset,
                        is_fees_pending = fees_pending,
                        is_follow_up_scheduled = follow_up
                    )
                )
            ]

        except (DatabaseCursorError, DatabaseExecutionError) as exc:
            raise VMDatabaseError(exc) from exc

    def getids(self, patient_id: str) -> list[str]:
        try:
            return self._repo.getids(patient_id)

        except (DatabaseCursorError, DatabaseExecutionError) as exc:
            raise VMDatabaseError(exc) from exc

    def getfields(
        self,
        visit_id: str,
        patient_id: bool = False,
        date: bool = False,
        diagnosis: bool = False,
        prescription: bool = False,
        notes: bool = False,
        fees_paid: bool = False,
        fees_pending: bool = False,
        follow_up_date: bool = False
    ) -> VisitManagerGetFieldsResult | None:
        if not visit_id:
            return None

        try:
            data = self._repo.getfields(
                visit_id = visit_id,
                patient_id = patient_id,
                date = date,
                diagnosis = diagnosis,
                prescription = prescription,
                notes = notes,
                fees_paid = fees_paid,
                fees_pending = fees_pending,
                follow_up_date = follow_up_date
            )

            if data is None:
                return None

            return VisitManagerGetFieldsResult(
                id = data.id,
                patient_id = data.patient_id,
                date = data.date,
                diagnosis = data.diagnosis,
                prescription = data.prescription,
                notes = data.notes,
                fees_paid = data.fees_paid,
                fees_pending = data.fees_pending,
                follow_up_date = data.follow_up_date
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
        try:
            self._validate_inputs(
                id = visit_id,
                date = date,
                fees_paid = fees_paid if fees_paid is not None else 0,
                fees_pending = fees_pending if fees_pending is not None else 0,
                follow_up_date = follow_up_date
            )

            self._repo.update(
                visit_id = visit_id,
                date = date,
                diagnosis = diagnosis,
                prescription = prescription,
                notes = notes,
                fees_paid = fees_paid,
                fees_pending = fees_pending,
                follow_up_date = follow_up_date
            )

        except (DatabaseCursorError, DatabaseExecutionError) as exc:
            raise VMDatabaseError(exc) from exc

        except DatabaseAbsentEntryError as exc:
            raise VMAbsentEntryError() from exc

    def genid(self) -> str:
        visit_id = generate_id(length = self._id_len)
        self._reserved_ids.append(visit_id)
        return visit_id

visit_manager: VisitManager | None = None

