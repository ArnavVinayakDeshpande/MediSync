"""
"""

import sqlite3 as sql3

from app.database.exceptions import *
from app.models.patient import Patient
from app.models.medical_condition import MedicalCondition
from app.common.converter import (
    date_to_db_fmt,
    date_from_db_fmt,
    age_to_date_range
)


class PatientRepository:
    def __init__(self, connection: sql3.Connection):
        self.connection = connection

        self._ensure_initialized()

    def _get_cursor(self):
        try:
            return self.connection.cursor()

        except sql3.Error as exc:
            raise DatabaseCursorError(exc) from exc

    def _ensure_initialized(self):
        cursor = self._get_cursor()

        try:
            cursor.execute(
            """
                    CREATE TABLE IF NOT EXISTS 
                           patients (
                               id TEXT PRIMARY KEY NOT NULL,
                               name TEXT NOT NULL,
                               dob TEXT,
                               number TEXT UNIQUE,
                               condition TEXT,
                               is_active INT
                           )
                """
            )

            self.commit()

        except sql3.Error as exc:
            raise DatabaseExecutionError(exc) from exc

        finally:
            cursor.close()

    def _create_patient(self, data: tuple) -> Patient:
        try:
            return Patient(
                id = data[0],
                name = data[1],
                dob = date_from_db_fmt(data[2]),
                number = data[3],
                condition = MedicalCondition(data[4]),
                is_active = data[5]
            )

        except Exception as exc:
            raise DatabaseParsingError() from exc

    def insert(self, patient: Patient):
        cursor = self._get_cursor() 

        try:
            cursor.execute(
                """
                    INSERT INTO 
                        patients (
                            id, 
                            name,
                            dob,
                            number,
                            condition,
                            is_active
                        )
                    VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    patient.id,
                    patient.name,
                    date_to_db_fmt(patient.dob),
                    patient.number,
                    patient.condition,
                    int(patient.is_active)
                )
            )

        except sql3.IntegrityError:
            raise DatabaseDuplicateEntryError() 

        except sql3.Error as exc:
            raise DatabaseExecutionError(exc) from exc

        finally:
            cursor.close()

    def delete(self, patient_id: str):
        cursor = self._get_cursor()

        try:
            cursor.execute(
                """
                    DELETE FROM patients WHERE id = ?
                """,
                (patient_id,)
            )

            if cursor.rowcount == 0:
                raise DatabaseAbsentEntryError()

        except sql3.Error as exc:
            raise DatabaseExecutionError(exc) from exc

        finally:
            cursor.close()

    def clear(self):
        cursor = self._get_cursor()

        try:
            cursor.execute(
                """
                    DELETE FROM patients
                """
            )

        except sql3.Error as exc:
            raise DatabaseExecutionError(exc) from exc

        finally:
            cursor.close()

    def get(self, patient_id: str) -> Patient | None:
        cursor = self._get_cursor()

        try:
            cursor.execute(
                """
                    SELECT * FROM patients WHERE id = ?
                """,
                    (patient_id,)
            )

            data = cursor.fetchone()

            if data is None:
                return None

            return self._create_patient(data)

        except sql3.Error as exc:
            raise DatabaseExecutionError(exc) from exc

        finally:
            cursor.close()

    def getall(
        self,
        size: int | None = None,
        offset: int | None = None,
        search: str | None = None,
        condition: MedicalCondition | None = None,
        active: bool | None = None,
        age: int | None = None
    ) -> list[Patient]:
        cursor = self._get_cursor()

        query = "SELECT * FROM patients"
        params = []
        filters = []

        try:
            if condition is not None:
                filters.append("condition = ?")
                params.append(condition.value)

            if active is not None:
                filters.append("is_active = ?")
                params.append(int(active))

            if search is not None:
                filters.append("name LIKE ?")
                params.append(search + "%")

            if age is not None:
                date_range = age_to_date_range(age)
                filters.append("dob >= ?")
                filters.append("dob <= ?")
                params.append(date_range[0])
                params.append(date_range[1])

            if filters:
                query += " WHERE " + " AND ".join(filters)

            query += " ORDER BY name DESC LIMIT ? OFFSET ?"
            params.append(size if size else -1)
            params.append(offset if offset is not None else 0)

            cursor.execute(
                query,
                params
            )

            data = cursor.fetchall()

            return [self._create_patient(d) for d in data]

        except sql3.Error as exc:
            raise DatabaseExecutionError(exc) from exc

        finally:
            cursor.close()

    def get_all_ids(self) -> list[str]:
        cursor = self._get_cursor()

        try:
            cursor.execute(
                """
                    SELECT id FROM patients
                """
            )

            return [row[0] for row in cursor.fetchall()]

        except sql3.Error as exc:
            raise DatabaseExecutionError(exc) from exc

    def get_name(self, patient_id: str) -> str | None:
        cursor = self._get_cursor()

        try:
            cursor.execute(
                """
                    SELECT name FROM patients WHERE id = ?
                """,
                (patient_id,)
            )

            return cursor.fetchone()

        except sql3.Error as exc:
            raise DatabaseExecutionError(exc) from exc

        finally:
            cursor.close()

    def get_id(self, patient_name: str) -> str | None:
        cursor = self._get_cursor()

        try:
            cursor.execute(
                """
                    SELECT id FROM patients WHERE name = ?
                """,
                (patient_name,)
            )

            return cursor.fetchone()

        except sql3.Error as exc:
            raise DatabaseExecutionError(exc) from exc

        finally:
            cursor.close()

    def update(self, patient: Patient):
        cursor = self._get_cursor()

        try:
            cursor.execute(
                """
                    UPDATE patients
                    SET 
                        name = ?,
                        dob = ?,
                        number = ?,
                        condition = ?,
                        is_active = ?
                    WHERE id = ?
                """,
                (
                    patient.name,
                    date_to_db_fmt(patient.dob),
                    patient.number,
                    patient.condition,
                    int(patient.is_active),
                    patient.id
                )
            )

            if cursor.rowcount == 0:
                raise DatabaseAbsentEntryError()

        except sql3.Error as exc:
            raise DatabaseExecutionError(exc) from exc

        finally:
            cursor.close()

    def exists(self, patient_id: str) -> bool:
        cursor = self._get_cursor()

        try:
            cursor.execute(
                """
                    SELECT name FROM patients WHERE id = ?
                """,
                (patient_id,)
            )

            return cursor.fetchone() is not None

        except sql3.Error as exc:
             raise DatabaseExecutionError(exc) from exc

        finally:
            cursor.close()

    def commit(self):
        try:
            self.connection.commit()

        except sql3.Error as exc:
            raise DatabaseExecutionError(exc) from exc

