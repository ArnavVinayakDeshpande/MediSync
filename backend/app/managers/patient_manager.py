"""

"""

from datetime import date as _date

from app.models.patient import Patient
from app.models.visit import Visit
from app.models.medical_condition import MedicalCondition
from app.database.database import database
from app.database.patient_md_repo import PatientMetadataRepo
from app.database.patient_visits_repo import PatientVisitsRepo
from app.database.exceptions import *
from .exceptions import *


class PatientManager:
    def __init__(self):
        self._metadata_repo = None
        self._visits_repo = None

        try:
            self._metadata_repo = database.patient_md_repo
            self._visits_repo = database.patient_visits_repo

        except Exception as exc:
            raise PMDatabaseError() from exc

        self._patient_id_count = 100001

    def _validate(self) -> None:
        if self._metadata_repo is None or self._visits_repo is None:
            raise PMDatabaseError()

    def _validate_metadata(self,
                           name: str,
                           dob: datetime,
                           number: str) -> None:
        if not name or not number:
            raise PMInvalidInputsError()

        if len(number) != 10:
            raise PMInvalidInputsError()

        try:
            _ = int(number)

        except ValueError:
            raise PMInvalidInputsError()

        # Maybe something for date as well

    def _validate_visit(self, fees_paid: float, fees_pending: float) -> None:
        if fees_paid < 0 or fees_pending < 0:
            raise PMInvalidInputsError()

    def _create_metadata(self,
                         name: str,
                         dob: _date,
                         number: str,
                         condition: MedicalCondition,
                         is_active: bool) -> PatientMetadata, int:

        self._validate_metadata(name, dob, number)

        id = 0

        return PatientMetadata(name=name,
                               dob=dob,
                               number=number,
                               condition=condition,
                               is_active=is_active), id

    def _create_visit(self,
                      id: int,
                      date: _date,
                      diagnosis: str,
                      prescription: str,
                      notes: str,
                      fees_paid: float,
                      fees_pending: float,
                      follow_up_date: _date | None) -> Visit:
        self._validate_visit(fees_paid, fees_pending)

        id = 0

        return Visit(id=id,
                     date=date,
                     diagnosis=diagnosis,
                     prescription=prescription,
                     notes=notes,
                     fees_paid=fees_paid,
                     fees_pending=fees_pending,
                     follow_up_date=follow_up_date)

    def create_patient_metadata(self,
                       name: str,
                       dob: _date,
                       number: str,
                       condition: MedicalCondition,
                       is_active: bool = True,
                       ) -> None:

        self._validate()

        self._validate_metadata(name, dob, number)

        patient_metadata, id  = self._create_metadata(name, dob, number, condition, is_active)

        try:
            self._metadata_repo.insert(patient_id=id,
                                       patient_metadata=patient_metadata)

        except DatabaseCursorError, DatabaseExecutionError as exc:
            raise PMDatabaseError from exc

        except DatabaseDuplicateEntryError:
            raise PMDuplicateEntryError()

        else:
            self._metadata_repo.commit()

    def create_visit(self,
                     patient_id: int,
                     date: _date,
                     diagnosis: str,
                     prescription: str,
                     notes: str,
                     fees_paid: float,
                     fees_pending: float,
                     follow_up_date = _date | None):
        self._validate()

        visit = self._visit()

        try:
             

        except DatabaseCursorError, DatabaseExecutionError as exc:
            raise PMDatabaseError from exc

        except DatabaseDuplicateEntryError:
            raise PMDuplicateEntryError()

        else:
            self._visits_repo.commit()

    def create_patient(self):
        pass

    def delete_patient(self):
        pass

    def delete_visit(self):
        pass

    def get_patient_metadata(self):
        pass

    def get_patient_visits(self):
        pass

    def get_patient(self):
        pass

    def edit_patient_metadata(self):
        pass

    def edit_patient_visit(self):
        pass

    def edit_patient(self):
        pass

    def get_all_patient_metadatas(self):
        pass

    def get_all_patient_visits(self):
        pass

    def get_all_patients(self):
        pass

