"""
"""

import sqlite3 as sql3

from app.models.visit import Visit
from app.common.converter import *
from .exceptions import *


class PatientVisitsRepo:
    def __init__(self, connection: sql3.Connection) -> None:
        self.connection = connection

        self._ensure_initialized()

    def _get_cursor(self) -> sql3.Cursor:
        try:
            return self.connection.cursor()

        except sql3.Error as exc:
            raise DatabaseCursorError() from exc

    def _ensure_initialized(self) -> None:
        cursor = self._get_cursor()

        try:
            self.connection.execute("""
                            PRAGMA foreign_keys = ON
                                    """)

            cursor.execute("""
                    CREATE TABLE IF NOT EXISTS
                           visits(
                               id INT PRIMARY KEY,
                               pid INT NOT NULL,
                               date TEXT,
                               diagnosis TEXT,
                               prescription TEXT,
                               notes TEXT,
                               fees_paid TEXT,
                               fees_pending TEXT,
                               follow_up_date TEXT,

                               FOREIGN KEY(pid)
                                REFERENCES patient_metadata(pid)
                                ON DELETE CASCADE
                               )
                           """)

            self.commit()

        except sql3.Error as exc:
            self.connection.rollback()
            raise DatabaseExecutionError(exc)

        finally:
            cursor.close()

    def _create_visit(self, data) -> Visit | None:
        if data is None:
            return None

        try:
            return Visit(id=data[0],
                         date=date_from_db_fmt(data[2]),
                         diagnosis=data[3],
                         prescription=data[4],
                         notes=data[5],
                         fees_paid=float(data[6]),
                         fees_pending=float(data[7]),
                         follow_up_date=date_from_db_fmt(data[8])
                         )

        except Exception as exc:
            raise DatabaseParsingError() from exc

    def commit(self) -> None:
        self.connection.commit()

    def insert(self, 
               patient_id: int,
               visit: Visit) -> None:
        cursor = self._get_cursor()

        try:
            cursor.execute("""
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
                           (visit.id,
                            patient_id,
                            date_to_db_fmt(visit.date),
                            visit.diagnosis,
                            visit.prescription,
                            visit.notes,
                            str(visit.fees_paid),
                            str(visit.fees_pending),
                            date_to_db_fmt(visit.follow_up_date)
                            )
                           )

        except sql3.IntegrityError:
            raise DatabaseDuplicateEntryError() 

        except sql3.Error as exc:
            raise DatabaseExecutionError(exc)

        finally:
            cursor.close()

    def delete(self, visit_id: int) -> None:
        cursor = self._get_cursor()

        try:
            cursor.execute("""
                    DELETE FROM visits WHERE id = ?
                           """,
                           (visit_id,)
                           )

            if cursor.rowcount == 0:
                raise DatabaseAbsentEntryError()

        except sql3.Error as exc:
            raise DatabaseExecutionError(exc)

        finally:
            cursor.close()

    def deleteall(self, patient_id: int) -> None:
        cursor = self._get_cursor()

        try:
            cursor.execute("""
                    DELETE FROM visits WHERE pid = ?
                           """,
                           (patient_id,)
                           )

        finally:
            cursor.close()

    def get(self, visit_id: int) -> Visit | None:
        cursor = self._get_cursor()

        try:
            cursor.execute("""
                    SELECT * FROM visits WHERE id = ?
                           """,
                           (visit_id,)
                           )

            return self._create_visit(cursor.fetchone())

        except sql3.Error as exc:
            raise DatabaseExecutionError(exc)

        finally:
            cursor.close()

    def getall(self, patient_id: int) -> list[Visit]:
        cursor = self._get_cursor()

        try:
            cursor.execute("""
                    SELECT * FROM visits WHERE pid = ?
                           """,
                           (patient_id,)
                           )

            data = cursor.fetchall()

            visits = []

            for d in data:
                visits.append(self._create_visit(d))

            return visits

        except sql3.Error as exc:
            raise DatabaseExecutionError(exc)

        finally:
            cursor.close()

    def update(self, visit: Visit) -> None:
        cursor = self._get_cursor()

        try:
            cursor.execute("""
                    UPDATE visits
                    SET date = ?, diagnosis = ?, prescription = ?,
                           notes = ?, fees_paid = ?, fees_pending = ?,
                           follow_up_date = ?
                    WHERE id = ?
                           """,
                           (date_to_db_fmt(visit.date),
                            visit.diagnosis,
                            visit.prescription,
                            visit.notes,
                            str(visit.fees_paid),
                            str(visit.fees_pending),
                            date_to_db_fmt(visit.follow_up_date),
                            visit.id
                           )
                           )

            if cursor.rowcount == 0:
                raise DatabaseAbsentEntryError()

        except sql3.Error as exc:
            raise DatabaseExecutionError(exc)

        finally:
            cursor.close()

