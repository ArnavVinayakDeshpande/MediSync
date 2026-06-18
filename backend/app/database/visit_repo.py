"""
"""

from datetime import date as _date
from dataclasses import dataclass
from pymongo.collection import Collection
from pymongo.errors import (
    PyMongoError,
    DuplicateKeyError
)

from app.database.exceptions import *
from app.models.visit import Visit
from app.common.converter import (
    date_to_db_fmt,
    date_from_db_fmt,
    visit_to_db_fmt,
    visit_from_db_fmt
)


type VisitRepositoryGetFieldsResult = dict[str, str | _date | float] | None

@dataclass
class VisitRepositoryGetResult:
    patient_id: str
    visit: Visit

class VisitRepository:
    def __init__(self, collection: Collection) -> None:
        self._collection = collection

        # Create the indices
        self._collection.create_index(
            "id",
            unique = True
        )

    @property
    def collection(self) -> Collection:
        return self._collection

    def insert(
        self,
        patient_id: str,
        visit: Visit
    ) -> None:
        try:
            self._collection.insert_one(
                document = visit_to_db_fmt(patient_id, visit)
            )

        except DuplicateKeyError as exc:
            raise DatabaseDuplicateEntryError() from exc

        except PyMongoError as exc:
            raise DatabaseExecutionError(exc) from exc
        
    def delete(self, visit_id: str) -> None:
        try:
            result = self._collection.delete_one(
                filter = {
                    "id": visit_id
                }
            )

            if result.deleted_count == 0:
                raise DatabaseAbsentEntryError()

        except PyMongoError as exc:
            raise DatabaseExecutionError(exc) from exc

    def deleteall(self, patient_id: str) -> None:
        try:
            result = self._collection.delete_many(
                filter = {
                    "pid": patient_id
                }
            )

            if result.deleted_count == 0:
                raise DatabaseAbsentEntryError()

        except PyMongoError as exc:
            raise DatabaseExecutionError(exc) from exc

    def get(self, visit_id: str) -> VisitRepositoryGetResult | None:
        try:
            visit = self._collection.find_one(
                filter = {
                    "id": visit_id
                }
            )

            if visit is None:
                return None

            data = visit_from_db_fmt(visit)

            return VisitRepositoryGetResult(
                patient_id = data[0],
                visit = data[1]
             )

        except PyMongoError as exc:
            raise DatabaseExecutionError(exc) from exc

    def getall(
        self,
        size: int = 0,
        offset: int = 0,
        patient_id: str | None = None,
        date: _date | None = None,
        is_fees_pending: bool | None = None,
        is_follow_up_scheduled: bool | None = None
    ) -> list[VisitRepositoryGetResult]:
        try:
            result = (
                self._collection
                .find(
                    {
                        **({"pid": patient_id} if patient_id else {}),
                        **({"date": date_to_db_fmt(date)} if date is not None else {}),
                        **({"fees_pending": {"$gt": 0.0} if is_fees_pending else {"$lte": 0.0}} if is_fees_pending is not None else {}),
                        **({"follow_up_date": {"$ne": None} if is_follow_up_scheduled else None} if is_follow_up_scheduled is not None else {})
                    }
                )
                .sort(
                    [
                        ("date", -1),
                        ("id", 1)
                    ]
                )
                .skip(offset)
                .limit(size)
            )

            return [
                VisitRepositoryGetResult(
                    patient_id = data[0],
                    visit = data[1]
                ) for data in [
                    visit_from_db_fmt(res) for res in result
                ]
            ]
            
        except PyMongoError as exc:
            raise DatabaseExecutionError(exc) from exc

    def getids(self, patient_id: str) -> list[str]:
        try:
            result = self._collection.find(
                {
                    "pid": patient_id
                },
                {
                    "_id": 0,
                    "id": 1
                }
            )

            return [res["id"] for res in result]
        
        except PyMongoError as exc:
            raise DatabaseExecutionError(exc) from exc

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
    ) -> VisitRepositoryGetFieldsResult:
        if not visit_id:
            return None
    
        query = {}

        query["_id"] = 0
        query["id"] = 1
        query["pid"] = int(patient_id)
        query["date"] = int(date)
        query["diagnosis"] = int(diagnosis)
        query["prescription"] = int(prescription)
        query["notes"] = int(notes)
        query["fees_paid"] = int(fees_paid)
        query["fees_pending"] = int(fees_pending)
        query["follow_up_date"] = int(follow_up_date)

        try:
            result = self._collection.find_one(
                {
                    "id": visit_id
                },
                query
            )

            if result is None:
                return None

            if date:
                result["date"] = date_from_db_fmt(result["date"])

            if follow_up_date:
                result["follow_up_date"] = date_from_db_fmt(result["follow_up_date"])

            return result

        except PyMongoError as exc:
            raise DatabaseExecutionError(exc) from exc

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
    ) -> None:
        clamp = lambda x, mi, mx: min(mx, max(mi, x))

        set_dict = {
            **({"date": date_to_db_fmt(date)} if date is not None else {}),
            **({"diagnosis": diagnosis} if diagnosis is not None else {}),
            **({"prescription": prescription} if prescription is not None else {}),
            **({"notes": notes} if notes is not None else {}),
            **({"fees_paid": clamp(fees_paid, 0, fees_paid)} if fees_paid is not None else {}),
            **({"fees_pending": clamp(fees_pending, 0, fees_pending)} if fees_pending is not None else {}),
            **({"follow_up_date": date_to_db_fmt(follow_up_date)} if follow_up_date is not None else {})
        }

        if not set_dict:
            # No values to update
            return

        try:
            result = self._collection.update_one(
                {
                    "id": visit_id
                },
                {
                    "$set": set_dict
                }
            )

            if result.matched_count == 0:
                raise DatabaseAbsentEntryError()

        except DuplicateKeyError as exc:
            raise DatabaseDuplicateEntryError() from exc

        except PyMongoError as exc:
            raise DatabaseExecutionError(exc) from exc

