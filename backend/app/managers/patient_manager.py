"""
"""

from datetime import date

from app.common.id_creater import generate_id
from app.database.database import Database
from app.database.exceptions import *
from app.database.patient_repo import PatientRepository
from app.models.patient import Patient
from app.models.medical_condition import MedicalCondition
from .exceptions import *


class PatientManager:
    def __init__(self, database: Database):
        self.database = database

        self._repo = self.database.patient_repo

        if self._repo is None:
            raise PMDatabaseError(DatabaseCursorError())

        self._reserved_ids: list[str] = []

    def _validate(self):
        if self._repo is None:
            raise PMDatabaseError(DatabaseCursorError())

    def _validate_inputs(
            self,
            name: str | None,
            dob: date | None,
            number: str | None):
        if name is not None:
            if not name:
                raise PMInvalidInputsError()

        if number is not None:
            if not number:
                raise PMInvalidInputsError()

            if len(number) != 10:
                raise PMInvalidInputsError()

            try:
                _ = int(number)

            except:
                raise PMInvalidInputsError()

    def create(
            self,
            patient: Patient) -> str:
        self._validate()

        try:
            # Check if it is a reserved id
            if patient.id in self._reserved_ids:
                self._reserved_ids.erase(patient.id)

            self._repo.insert(patient)

        except (DatabaseCursorError, DatabaseExecutionError) as exc:
            self._rollback_id()
            raise PMDatabaseError(exc) from exc

        except DatabaseDuplicateEntryError as exc:
            self._rollback_id()
            raise PMDuplicateEntryError() from exc

        else:
            self._repo.commit()
            return patient.id

    def delete(self, patient_id: str):
        self._validate()

        try:
            self._repo.delete(patient_id)

        except (DatabaseCursorError, DatabaseExecutionError) as exc:
            raise PMDatabaseError(exc) from exc

        except DatabaseAbsentEntryError as exc:
            raise PMAbsentEntryError() from exc

        else:
            self._repo.commit()

    def clear(self):
        self._validate()

        try:
            self._repo.clear()

        except (DatabaseCursorError, DatabaseExecutionError) as exc:
            raise PMDatabaseError(exc) from exc

        else:
            self._repo.commit()

    def get(self, patient_id: str) -> Patient | None:
        self._validate()

        try:
            return self._repo.get(patient_id)

        except (DatabaseCursorError, DatabaseExecutionError) as exc:
            raise PMDatabaseError(exc) from exc

    def getall(self):
        self._validate()

        try:
            return self._repo.getall()

        except (DatabaseCursorError, DatabaseExecutionError) as exc:
            raise PMDatabaseError(exc) from exc

    def update(
            self,
            patient_id: str,
            name: str | None = None,
            dob: date | None = None,
            number: str | None = None,
            condition: MedicalCondition | None = None,
            is_active: bool | None = None):
        self._validate()

        try:
            self._validate_inputs(name, dob, number)

            patient = self.get(patient_id)

            if patient is None:
                raise PMAbsentEntryError()

            patient.name = name if name else patient.name
            patient.dob = dob if dob else patient.dob
            patient.number = number if dob else patient.number
            patient.condition = condition if condition else patient.condition
            patient.is_active = is_active if is_active else patient.is_active

            self._repo.update(patient)

        except (DatabaseCursorError, DatabaseExecutionError) as exc:
            raise PMDatabaseError(exc) from exc

        except DatabaseAbsentEntryError as exc:
            raise PMAbsentEntryError() from exc

        else:
            self._repo.commit()

    def exists(self, patient_id: str) -> bool:
        self._validate()

        try:
            return self._repo.exists(patient_id)

        except (DatabaseCursorError, DatabaseExecutionError) as exc:
            raise PMDatabaseError(exc) from exc

    def create_id(self) -> str:
        id = generate(length=6)

        self._reserved_ids.append(id)

        return id


patient_manager: PatientManager | None = None

