"""

"""

import sqlite3 as sql3

from app.models.patient import PatientMetadata
from app.common.converter import *
from .exceptions import *


class PatientMetadataRepo:
    def __init__(self, connection: sql3.Connection) -> None:
        self.connection = connection

        self._ensure_initialized()

    def _get_cursor(self) -> sql3.Cursor:
        cursor = self.connection.cursor()

        if cursor is None:
            raise DatabaseCursorError()

        return cursor

    def _ensure_initialized(self) -> None:
        cursor = self._get_cursor()

        try:
            cursor.execute("""
                    CREATE TABLE IF NOT EXISTS 
                           patient_metadata (
                               pid INT PRIMARY KEY,
                               name TEXT NOT NULL,
                               dob TEXT,
                               number TEXT,
                               is_active INT
                               )
                           """)

        except sql3.Error as exc:
            raise DatabaseExecutionError(exc)

        finally:
            cursor.close()

    def _create_metadata(self, data) -> PatientMetadata | None:
        if data is None:
            return None

        try:
            return PatientMetadata(name=data[1],
                                   dob=date_from_db_fmt(data[2]),
                                   number=data[3],
                                   is_active=bool(data[4])
                                   )

        except Exception as exc:
            raise PatientMDRepoParsingError() from exc

    def commit(self) -> None:
        self.connection.commit()

    def insert(self,
               patient_id: int,
               patient_metadata: PatientMetadata) -> None:
        cursor = self._get_cursor()

        try:
            cursor.execute("""
                    INSERT INTO patient_metadata(
                        pid, 
                        name,
                        dob,
                        number,
                        is_active
                        )
                    VALUES (?, ?, ?, ?, ?)
                           """,
                           (patient_id,
                            patient_metadata.name,
                            date_to_db_fmt(patient_metadata.dob),
                            patient_metadata.number,
                            int(patient_metadata.is_active)
                           )
                           )

        except sql3.IntegrityError:
            raise DatabaseDuplicateEntryError()

        except sql3.Error as exc:
            raise DatabaseExecutionError(exc)

        finally:
            cursor.close()

    def delete(self, patient_id: int) -> None:
        cursor = self._get_cursor()

        try:
            cursor.execute("""
                    DELETE FROM patient_metadata WHERE pid = ?
                           """,
                           (patient_id,)
                           )

            if cursor.rowcount == 0:
                raise DatabaseAbsentEntryError()

        except sql3.Error as exc:
            raise DatabaseExecutionError(exc)

        finally:
            cursor.close()

    def get(self, patient_id: int) -> PatientMetadata | None:
        cursor = self._get_cursor()

        try:
            cursor.execute("""
                    SELECT * FROM patient_metadata WHERE pid = ?
                           """,
                           (patient_id,)
                           )

            data = cursor.fetchone()

            return self._create_metadata(data)

        except sql3.Error as exc:
            raise DatabaseExecutionError(exc)

        finally:
            cursor.close()

    def getall(self) -> list[PatientMetadata]:
        cursor = self._get_cursor()

        try:
            cursor.execute("""
                    SELECT * FROM patient_metadata
                           """)

            data = cursor.fetchall()

            values = []

            for d in data:
                values.append(self._create_metadata(d))

            return values

        except sql3.Error as exc:
            raise DatabaseExecutionError(exc)

        finally:
            cursor.close()

    def update(self,
               patient_id: int,
               patient_metadata: PatientMetadata) -> None:
        cursor = self._get_cursor()

        try:
            cursor.execute("""
                    UPDATE patient_metadata
                    SET name = ?, dob = ?, number = ?, is_active = ?
                    WHERE pid = ?
                           """,
                           (patient_metadata.name,
                            date_to_db_fmt(patient_metadata.dob),
                            patient_metadata.number,
                            int(patient_metadata.is_active),
                            patient_id
                           )
                           )
            
            if cursor.rowcount == 0:
                raise DatabaseAbsentEntryError()

        except sql3.Error as exc:
            raise DatabaseExecutionError(exc)

        finally:
            cursor.close()

