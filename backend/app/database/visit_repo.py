"""
"""

import sqlite3 as sql3

from app.models.visit import Visit
from app.common.converter import *
from app.database.exceptions import *


class VisitRepository:
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
            self.connection.execute(
                """
                PRAGMA foreign_keys = ON
                """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS
                    visits (
                        id TEXT PRIMARY KEY NOT NULL,
                        pid TEXT,
                        date TEXT,
                        diagnosis TEXT,
                        prescription TEXT,
                        notes TEXT,
                        fees_paid INT,
                        fees_pending INT,
                        follow_up_date TEXT,

                        FOREIGN KEY (pid) REFERENCES patients (id)
                            ON DELETE CASCADE
                    )
                """
            )

        except sql3.Error as exc:
            raise DatabaseExecutionError(exc) from exc

        finally:
            cursor.close()

    def _create_visit(self, data: tuple | None) -> Visit | None:
        if data is None:
            return None

        try:
            return Visit(
                id=data[0],
                date=date_from_db_fmt(data[2]),
                diagnosis=data[3],
                prescription=data[4],
                notes=data[5],
                fees_paid=float(data[6]) / 100,
                fees_pending=float(data[7]) / 100,
                follow_up_date=date_from_db_fmt(data[8]),
            )

        except Exception as exc:
            raise DatabaseParsingError(exc) from exc

    def insert(self, patient_id: str, visit: Visit):
        cursor = self._get_cursor()

        try:
            cursor.execute(
                """
                INSERT INTO visits (
                    id,
                    pid,
                    date,
                    diagnosis,
                    prescription,
                    notes,
                    fees_paid,
                    fees_pending,
                    follow_up_date
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    visit.id,
                    patient_id,
                    date_to_db_fmt(visit.date),
                    visit.diagnosis,
                    visit.prescription,
                    visit.notes,
                    int(visit.fees_paid * 100),
                    int(visit.fees_pending * 100),
                    date_to_db_fmt(visit.follow_up_date),
                ),
            )

        except sql3.IntegrityError as exc:
            raise DatabaseDuplicateEntryError() from exc

        except sql3.Error as exc:
            raise DatabaseExecutionError(exc) from exc

        finally:
            cursor.close()

    def delete(self, visit_id: str):
        cursor = self._get_cursor()

        try:
            cursor.execute(
                """
                DELETE FROM visits WHERE id = ?
                """,
                (visit_id,),
            )

            if cursor.rowcount == 0:
                raise DatabaseAbsentEntryError()

        except sql3.Error as exc:
            raise DatabaseExecutionError(exc) from exc

        finally:
            cursor.close()

    def deleteall(self, patient_id: str):
        cursor = self._get_cursor()

        try:
            cursor.execute(
                """
                DELETE FROM visits WHERE pid = ?
                """,
                (patient_id,),
            )

        except sql3.Error as exc:
            raise DatabaseExecutionError(exc) from exc

        finally:
            cursor.close()

    def clear(self):
        cursor = self._get_cursor()

        try:
            cursor.execute(
                """
                DELETE FROM visits
                """
            )

        except sql3.Error as exc:
            raise DatabaseExecutionError(exc) from exc

        finally:
            cursor.close()

    def get(self, visit_id: str) -> Visit | None:
        cursor = self._get_cursor()

        try:
            cursor.execute(
                """
                SELECT * FROM visits WHERE id = ?
                """,
                (visit_id,),
            )

            data = cursor.fetchone()

            return self._create_visit(data)

        except sql3.Error as exc:
            raise DatabaseExecutionError(exc) from exc

        finally:
            cursor.close()

    def getall(
            self,
            patient_id: str | None = None,
            size: int | None = None,
            offset: int | None = None ,
            fees_pending: bool | None = None,
            follow_up: bool | None = None
            ) -> list[Visit]:
        cursor = self._get_cursor()

        query = "SELECT * FROM visits"
        params = []
        filters = []

        try:
            if patient_id:
                filters.append(" pid = ?")
                params.append(patient_id)

            if fees_pending is not None:
                if fees_pending:
                    filters.append(" fees_pending > 0")
                else:
                    filters.append(" fees_pending = 0")

            if follow_up is not None:
                if follow_up:
                    filters.append(" follow_up_date IS NOT NULL")
                else:
                    filters.append(" follow_up_date IS NULL")

            if filters:
                query += " WHERE " + " AND ".join(filters)

            query += " ORDER BY date DESC LIMIT  ? OFFSET  ?"
            params.append(size if size else -1)
            params.append(offset if offset is not None else 0)

            cursor.execute(
                    query,
                    params
            )

            data = cursor.fetchall()

            return [self._create_visit(d) for d in data]

        except sql3.Error as exc:
            raise DatabaseExecutionError(exc) from exc

        finally:
            cursor.close()

    def update(self, visit: Visit):
        cursor = self._get_cursor()

        try:
            cursor.execute(
                """
                UPDATE visits
                SET
                    date = ?,
                    diagnosis = ?,
                    prescription = ?,
                    notes = ?,
                    fees_paid = ?,
                    fees_pending = ?,
                    follow_up_date = ?
                WHERE id = ?
                """,
                (
                    date_to_db_fmt(visit.date),
                    visit.diagnosis,
                    visit.prescription,
                    visit.notes,
                    int(visit.fees_paid * 100),
                    int(visit.fees_pending * 100),
                    date_to_db_fmt(visit.follow_up_date),
                    visit.id,
                ),
            )

            if cursor.rowcount == 0:
                raise DatabaseAbsentEntryError()

        except sql3.Error as exc:
            raise DatabaseExecutionError(exc) from exc

        finally:
            cursor.close()

    def exists(self, visit_id: str) -> bool:
        cursor = self._get_cursor()

        try:
            cursor.execute(
                    """
                    SELECT 1 FROM visits WHERE id = ?
                    """,
                    (visit_id,)
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

