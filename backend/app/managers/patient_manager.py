"""
"""

from app.database.database import Database
from app.database.patient_repo import PatientRepository


class PatientManager:
    def __init__(self, database: Database):
        self.database = database

        self._repo = self.database.patient_repo

        if self._repo is None:
            raise PMDatabaseError()

        self._last_id = self._get_last_id()

    def _get_last_id(self):
        try:
            ids = self._repo.getids()

            return max(ids) + 1 if ids else 1

        except (DatabaseCursorError, DatabasExecutionError) as exc:
            raise PMDatabaseError() from exc

    def _rollback_id(self):
        self._last_id -= 1

    def _validate(self):
        if self._repo is None:
            raise PMDatabaseError()

    def _validate_inputs(self, name: str, dob: date | None, number: str):
        if not name or not number:
            raise PMInvalidInputsError()

        if len(number) != 10:
            raise PMInvalidInputsError()

        try:
            _ = int(number)

        except Exception:
            raise PMInvalidInputsError()

    def _create_patient(
            self,
            name: str,
            dob: date | None,
            number: str,
            condition: str,
            is_active: bool) -> Patient:
        self._validate_inputs(name, dob, number)

        patient_id = self._last_id
        self._last_id += 1

        return Patient(
                id = patient_id,
                name = name,
                dob = dob,
                number = number,
                condition = condition,
                is_active = is_active
                )

    def create(
            self,
            name: str,
            dob: date | None,
            number: str,
            condition: str,
            is_active: bool):
        self._validate()

        try:
            self._repo.insert(self._create_patient(
                name,
                dob,
                number,
                condition,
                is_active
                ))

        except (DatabaseCursorError, DatabaseExecutionError) as exc:
            self._rollback_id()
            raise PMDatabaseError() from exc

        except DatabaseDuplicateEntryError:
            self._rollback_id()
            raise PMDuplicateEntryError()

        else:
            self._repo.commit()


    def delete(self, patient_id: int):
        self._validate()

        try:
            self._repo.delete(patient_id)

        except (DatabaseCursorError, DatabaseExecutionError) as exc:
            raise PMDatabaseError() from exc

        except DatabaseAbsentEntryError:
            raise PMAbsentEntryError()

        else:
            self._repo.commit()

    def clear(self):
        self._validate()
        
        try:
            self._repo.clear()

        except (DatabaseCursorError, DatabaseExecutionError) as exc:
            raise PMDatabaseError() from exc

        else:
            self._repo.commit()

    def get(self, patient_id: int) -> Patient | None:
        self._validate()

        try:
            return self._repo.get(patient_id)

        except (DatabaseCursorError, DatabaseExecutionError) as exc:
            raise PMDatabaseError() from exc

    def getall(self):
        self._validate()

        try:
            return self._repo.getall()

        except (DatabaseCursorError, DatabaseExecutionError) as exc:
            raise PMDatabaseError() from exc

    def update(self, patient: Patient):
        self._validate()

        try:
            self._repo.update(patient)

        except (DatabaseCursorError, DatabaseExecutionError) as exc:
            raise PMDatabaseError() from exc

        except DatabaseAbsentEntryError:
            raise PMAbsentEntryError()

        else:
            self._repo.commit()

patient_manager: PatientManager | None = None

