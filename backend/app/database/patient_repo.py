"""
"""

from datetime import date
from pymongo.collection import Collection
from pymongo.errors import (
    PyMongoError,
    DuplicateKeyError
)

from app.database.exceptions import *
from app.models.patient import Patient
from app.models.medical_condition import MedicalCondition
from app.common.converter import (
    date_to_db_fmt,
    date_from_db_fmt,
    patient_to_db_fmt,
    patient_from_db_fmt,
    age_to_date_range
)


type PatientRepositoryGetFieldsResult = dict[str, str | date | MedicalCondition | bool] | None

class PatientRepository:
    def __init__(self, collection: Collection) -> None:
        self._collection = collection

        # Create the indices
        self._collection.create_index(
            "id",
            unique = True
        )

        self._collection.create_index(
            keys = "number",
            unique = True
        )
    
    @property
    def collection(self) -> Collection:
        return self._collection

    def insert(
        self,
        patient: Patient
    ) -> None:
        try:
            self._collection.insert_one(
                document = patient_to_db_fmt(patient = patient)
            ) 

        except DuplicateKeyError as exc:
            raise DatabaseDuplicateEntryError() from exc

        except PyMongoError as exc:
            raise DatabaseExecutionError(exc) from exc

    def delete(self, patient_id: str) -> None:
        try:
            result = self._collection.delete_one(
                filter = {
                    "id": patient_id
                }
            )
            
            if result.deleted_count == 0:
                raise DatabaseAbsentEntryError()

        except PyMongoError as exc:
            raise DatabaseExecutionError(exc) from exc

    def get(self, patient_id: str) -> Patient | None:
        try:
            patient = self._collection.find_one(
                filter = {
                    "id": patient_id
                }
            )

            return patient_from_db_fmt(patient) if patient is not None else None

        except PyMongoError as exc:
            raise DatabaseExecutionError(exc) from exc

    def getall(
        self,
        size: int = 0,
        offset: int = 0,
        condition: MedicalCondition | None = None,
        is_active: bool | None = None,
        age: int | None = None
    ) -> list[Patient]:
        query = {}

        if condition is not None:
            query["condition"] = condition.value

        if is_active is not None:
            query["is_active"] = is_active

        if age is not None:
            date_range = age_to_date_range(age)

            query["dob"] = {
                "$lte": date_range[1],
                "$gte": date_range[0]
            }

        try:
            result = (
                self._collection
                .find(query)
                .sort(
                    [
                        ("name", 1),
                        ("id", 1)
                    ]
                )
                .skip(offset)
                .limit(size)
            )

            return [
                patient_from_db_fmt(patient) for patient in result
            ]

        except PyMongoError as exc:
            raise DatabaseExecutionError(exc) from exc

    def getid(self, patient_name: str) -> str | None:
        if not patient_name:
            return None

        try:
           result = self._collection.find_one(
                {
                    "name": patient_name
                },
                {
                    "id": 1,
                    "_id": 0
                }
            ) 

           return result["id"] if result else None

        except PyMongoError as exc:
            raise DatabaseExecutionError(exc) from exc

    def getfields(
        self,
        patient_id: str,
        name: bool = False,
        dob: bool = False,
        number: bool = False,
        condition: bool = False,
        is_active: bool = False
    ) -> PatientRepositoryGetFieldsResult:
        if not patient_id:
            return None

        query = {}

        query["_id"] = 0
        query["id"] = 1
        query["name"] = int(name)
        query["dob"] = int(dob)
        query["number"] = int(number)
        query["condition"] = int(condition)
        query["is_active"] = int(is_active)

        try:
            result = self._collection.find_one(
                {
                    "id": patient_id
                },
                query
            )

            if result is None:
                return None

            if dob:
                result["dob"] = date_from_db_fmt(result["dob"])

            if condition:
                result["condition"] = MedicalCondition(result["condition"])

            if is_active:
                result["is_active"] = bool(result["is_active"])

            return result

        except PyMongoError as exc:
            raise DatabaseExecutionError(exc) from exc
    

    def update(
        self,
        patient_id: str,
        name: str | None = None,
        dob: date | None = None,
        number: str | None = None,
        condition: MedicalCondition | None = None,
        is_active: bool | None = None
    ) -> None:
        set_dict = {
            **({"name": name} if name else {}),
            **({"dob": date_to_db_fmt(dob)} if dob is not None else {}),
            **({"number": number} if number else {}),
            **({"condition": condition.value} if condition is not None else {}),
            **({"is_active": is_active} if is_active is not None else {})
        }

        if not set_dict:
            # No values to update
            return

        try:
            result = self._collection.update_one(
                {
                    "id": patient_id
                },
                {
                    "$set":  set_dict
                }
            )

            if result.matched_count == 0:
                raise DatabaseAbsentEntryError()

        except DuplicateKeyError as exc:
            raise DatabaseDuplicateEntryError() from exc

        except PyMongoError as exc:
            raise DatabaseExecutionError(exc) from exc

