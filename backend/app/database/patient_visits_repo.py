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

    def _get_cursor(self) -> None:
        try:
            return self.connection.cursor()

        except sql3.Error as exc:
            raise DatabaseCursorError() from exc

    def _ensure_initialized(self) -> none:
        cursor = self._get_cursor()

        try:
            cursor.execute("""
                    PRAGMA FOREIGN_KEYS = ON
                           """)

            cursor.execute("""
                    CREATE TABLE IF NOT EXIST 
                           visits(
                               id INT PRIMARY KEY,
                               pid INT,
                               date TEXT,
                               diagnosis TEXT,
                               prescription TEXT,
                               notes TEXT,
                               fees_paid TEXT,
                               fees_pending TEXT,
                               follow_up_date TEXT

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

    def commit(self) -> None:
        self.conneciton.commit()

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
                            str(visit.fes)
                            )
                           )

        except sql3.IntegrityError:
            raise DatabaseDuplicateEntryError() 

        except sql3.Error as exc:
            raise DatabaseExecutionError(exc)

        finally:
            cursor.close()

    def delete(self):
        pass

    def get(self):
        pass

    def getall(self):
        pass

    def update(self):
        pass

