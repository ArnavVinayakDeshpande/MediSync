"""
"""

import sqlite3 as sql3

from .exceptions import *
from app.models.patient import Patient
from app.common.converter import *


class PatientRepository:
    def __init__(self, connection: sql3.Connection):
        self.connection = connection

        self._ensure_initialized()

    def _get_cursor(self):
        try:
            return self.connection.cursor()

        except sql3.Error as exc:
            raise DatabaseCursorError() from exc

    def _ensure_initialized(self):
        cursor = self._get_cursor()

        try:
            cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS 
                           patients (
                               id INT PRIMARY KEY,
                               name TEXT NOT NULL,
                               dob TEXT,
                               number TEXT UNIQUE,
                               condition TEXT,
                               is_active INT
                               )
                    """)

            self.commit()

        except sql3.Error as exc:
            raise DatabaseExecutionError(exc)

        finally:
            cursor.close()

    def _create_patient(self, data: tuple | None) -> Patient | None:
        if not data:
            return None

        try:
            return Patient(
                    id = data[0],
                    name = data[1],
                    dob = date_from_db_fmt(data[2]),
                    number = data[3],
                    condition = data[4],
                    is_active = data[5]
                    )

        except Exception as exc:
            raise DatabaseParsingError() from exc

    def insert(self, patient: Patient):
        cursor = self._get_cursor() 

        try:
            cursor.execute(
                    """
                    INSERT INTO patients (
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

        except sql3.Error as exc:
            raise DatabaseExecutionError(exc)

        finally:
            cursor.close()

    def delete(self, patient_id: int):
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
            raise DatabaseExecutionError(exc)

        finally:
            cursor.close()

    def clear(self):
        cursor = self._get_cursor()

        try:
            cursor.execute(
                    """
                    DELETE * FROM patients
                    """
                    )

        except sql3.Error as exc:
            raise DatabaseExecutionError(exc)

        finally:
            cursor.close()

    def get(self, patient_id: int) -> Patient | None:
        cursor = self._get_cursor()

        try:
            cursor.execute(
                    """
                    SELECT * FROM patients WHERE id = ?
                    """,
                    (patient_id,)
                    )

            data = cursor.fetchone()

            return self._create_patient(data)

        except sql3.Error as exc:
            raise DatabaseExecutionError(exc)

        finally:
            cursor.close()

    def getall(self) -> list[Patient]:
        cursor = self._get_cursor()

        try:
            cursor.execute(
                    """
                    SELECT * FROM patients
                    """
                    )

            data = cursor.fetchall()

            patients = []

            for d in data:
                patients.append(self._create_patient(d))

            return patients

        except sql3.Error as exc:
            raise DatabaseExecutionError(exc)

        finally:
            cursor.close()

    def getids(self) -> list[int]:
        cursor = self._get_cursor()

        try:
            cursor.execute(
                    """
                    SELECT id FROM patients
                    """
                    )

            return [row[0] for row in cursor.fetchall()]

        except sql3.Error as exc:
            raise DatabaseExecutionError(exc)

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
            raise DatabaseExecutionError(exc)

        finally:
            cursor.close()

    def commit(self):
        try:
            self.connection.commit()

        except sql3.Error as exc:
            raise DatabaseExecutionError(exc)

