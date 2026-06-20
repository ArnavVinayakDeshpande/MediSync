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

        try:
            self._repo: PatientRepository = self.database.patient_repository
        except DatabaseDisconnectedError as exc:
            raise PMDatabaseError(exc) from exc

        self._reserved_ids: list[str] = []

        self._id_len = 6

    def _validate_inputs(
        self,
        id: str | None,
        name: str | None,
        dob: date | None,
        number: str | None
    ):
        if id is not None:
            if not id:
                raise PMInvalidInputsError()

            if len(id) != self._id_len:
                raise PMInvalidInputsError()

            if id != id.upper():
                raise PMInvalidInputsError()

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
        patient: Patient
    ) -> str:
        try:
            # Check if it is a reserved id
            if patient.id in self._reserved_ids:
                self._reserved_ids.remove(patient.id)

            self._repo.insert(patient)

        except (DatabaseCursorError, DatabaseExecutionError) as exc:
            raise PMDatabaseError(exc) from exc

        except DatabaseDuplicateEntryError as exc:
            raise PMDuplicateEntryError() from exc

        else:
            return patient.id

    def delete(self, patient_id: str):
        try:
            self._repo.delete(patient_id)

        except (DatabaseCursorError, DatabaseExecutionError) as exc:
            raise PMDatabaseError(exc) from exc

        except DatabaseAbsentEntryError as exc:
            raise PMAbsentEntryError() from exc

    def get(self, patient_id: str) -> Patient | None:
        try:
            return self._repo.get(patient_id)

        except (DatabaseCursorError, DatabaseExecutionError) as exc:
            raise PMDatabaseError(exc) from exc

    def getall(
        self,
        size: int = 0,
        offset: int = 0,
        search: str | None = None,
        condition: MedicalCondition | None = None,
        active: bool | None = None,
        age: int | None = None
    ):
        try:
            return self._repo.getall(
                size = size,
                offset = offset,
                search = search,
                condition = condition,
                is_active = active,
                age = age
            )

        except (DatabaseCursorError, DatabaseExecutionError) as exc:
            raise PMDatabaseError(exc) from exc

    def getid(self, patient_name: str) -> str | None:
        try:
            return self._repo.getid(patient_name)

        except (DatabaseCursorError, DatabaseExecutionError) as exc:
            raise PMDatabaseError(exc) from exc

    def update(
        self,
        patient_id: str,
        name: str | None = None,
        dob: date | None = None,
        number: str | None = None,
        condition: MedicalCondition | None = None,
        is_active: bool | None = None
    ) -> None:
        try:
            self._validate_inputs(patient_id, name, dob, number)

            self._repo.update(
                patient_id = patient_id,
                name = name,
                dob = dob,
                number = number,
                condition = condition,
                is_active = is_active
            )

        except (DatabaseCursorError, DatabaseExecutionError) as exc:
            raise PMDatabaseError(exc) from exc

        except DatabaseAbsentEntryError as exc:
            raise PMAbsentEntryError() from exc

    def genid(self) -> str:
        id = generate_id(length = self._id_len)

        self._reserved_ids.append(id)

        return id


patient_manager: PatientManager | None = None

