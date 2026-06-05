"""
"""

import sqlite3 as sql3
from models.patient import *
from .exceptions import *
from app.common.converter import *


class PatientRepoParseError(Exception):
    _MESSAGE = "Failed to parse patient information from database."

    def __init__(self) -> None:
        super().__init__(self._MESSAGE)

    def message(self) -> str:
        return self._MESSAGE

class PatientRepository:
    def __init__(self, connection: sql3.Connection) -> None:
        self.connection: sql3.Connection = connection

        await self._ensure_initialized()

    def _get_cursor(self) -> sql3.Cursor:
        cursor = self.connection.cursor()

        if cursor is None:
            raise DatabaseCursorError()

        return cursor

    def _create_visit(self, data) -> Visit:
        try:
            visit = Visit(id=data[0],
                          date=converter.date_from_db_fmt(data[2]),
                          diagnosis=data[3],
                          prescription=data[4],
                          notes=data[5],
                          fees_paid=float(data[6]),
                          fees_remaining=float(data[7]),
                          follow_up_date=converter.date_from_db_fmt(data[8])
                          )
            return visit

        except:
            raise PatientRepoParseError()

    def _create_patient(self, data_pat, data_visit) -> Patient:
        try:
            visits = []

            for visit_data in data_visit:
                visits.append(self._create_visit(visit_data))

            patient = Patient(id=data_pat[0],
                              name=data_pat[1],
                              dob=converter.date_from_db_fmt(data[2]),
                              number=data_pat[3],
                              is_active=bool(data_pat[4]),
                              total_fees_paid=str(data_pat[5]),
                              fees_remaining=str(data_pat[6]),
                              condition=data_pat[7],
                              visits=visits)

            return patient


        except:
            raise PatientRepoParseError()

    async def _ensure_initialized(self) -> None:
        cursor = self._get_cursor()

        try:
            cursor.execute("""
                    CREATE TABLE IF NOT EXISTS patients (
                        id INT PRIMARY KEY UNIQUE,
                        name TEXT NOT NULL,
                        dob TEXT,
                        number TEXT NOT NULL UNIQUE,
                        is_active INT,
                        total_fees_paid TEXT NOT NULL,
                        fees_remaining TEXT NOT NULL,
                        condition TEXT,
                        num_visits INT
                        )
                           """)

            cursor.execute("""
                    CREATE TABLE IF NOT EXISTS visits (
                        id INT PRIMARY KEY UNIQUE ,
                        patient_id INT,
                        date TEXT NOT NULL,
                        diagnosis TEXT,
                        prescription TEXT,
                        notes TEXT,
                        fees_paid TEXT NOT NULL,
                        fees_remaining TEXT NOT NULL,
                        follow_up_date TEXT
                        )
                           """)

        except sql3.Error as exc:
            raise DatabaseExecutionError(exc)

        else:
            self.commit()

        finally:
            cursor.close()

    async def insert(self, patient: Patient) -> None:
        cursor = self._get_cursor()

        try:
            # Insert into patients table
            cursor.execute("""
                    INSERT INTO patients (
                        id, name, dob, number,
                        is_active, total_fees_paid,
                        fees_remaining, condition,
                        num_visits
                        )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                           """,
                           (
                               patient.id,
                               patient.name,
                               converter.date_to_db_fmt(patient.dob),
                               patient.number,
                               patient.is_active,
                               str(patient.total_fees_paid),
                               str(patient.fees_remaining),
                               condition,
                               len(patient.visits)
                               )
                           )

            # Insert any visits
            for visit in patient.visits:
                cursor.execute("""
                        INSERT INTO visits (
                            id, patient_id, date,
                            diagnosis, prescription, notes,
                            fees_paid, fees_remaining, follow_up_date
                            )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                               """,
                               (
                                   visit.id,
                                   patient.id,
                                   converter.date_to_db_fmt(visit.date),
                                   visit.diagnosis,
                                   visit.prescription,
                                   visit.notes,
                                   str(visit.fees_paid),
                                   str(visit.fees_remaining),
                                   converter.date_to_db_fmt(visit.follow_up_date)
                                   )
                               )

        except sql3.IntegrityError:
            raise DatabaseDuplicateEntryError()

        except sql3.Error as exc:
            raise DatabaseExecutionError(exc)

        finally:
            cursor.close()

    async def delete(self, patient_id: int) -> None:
        cursor = self._get_cursor()

        try:
            # Delete the patient
            cursor.execute("""
                    DELETE FROM patients WHERE id = ?
                           """,
                           (patient_id)
                           )

            # Delete the visits
            cursor.execute("""
                    DELETE FROM visits WHERE patient_id = ?
                           """,
                           (patient_id)
                           )

            if cursor.rowcount == 0:
                raise DatabaseAbsentEntryError()

        except sql3.Error as exc:
            raise DatabaseExecutionError(exc)

        finally:
            cursor.close()

    async def update(self, patient: Patient) -> None:
        cursor = self._get_cursor()

        try:
            # Get all visit ids 
            cursor.execute("""
                    SELECT id FROM visits WHERE patient_id = ?
                           """,
                           (patient.id)
                           )
            

            # Update patient
            cursor.execute("""
                    UPDATE patients 
                    SET name = ?, dob = ?, number = ?,
                        is_active = ?, total_fees_paid = ?, 
                        fees_remaining = ?, condition = ?
                    WHERE id = ?
                           """,
                           (
                               patient.name,
                               converter.date_to_db_fmt(patient.dob),
                               patient.number,
                               patient.is_active,
                               str(patient.total_fees_paid),
                               str(patient.fees_remaining),
                               patient.condition
                               )
                           )


            # Update visits

            if cursor.rowcount == 0:
                raise DatabaseAbsentEntryError()

        except sql3.Error as exc:
            raise DatabaseExecutionError(exc)

        finally:
            cursor.close()

    async def get(self, patient_id: int) -> Patient | None:
        cursor = self._get_cursor()

        try:
            # Select from patients
            cursor.execute("""
                    SELECT * FROM patients WHERE id = ?
                           """,
                           (patient_id)
                           )

            patient_data = cursor.fetchone()

            # Select from visits
            cursor.execute("""
                    SELECT * from visits WHERE patient_id = ?
                           """,
                           (patient_id)
                           )

            visits_data = cursor.fetchall()
            patient_data = cursor.fetchone()

            return self._create_patient(patient_data, visits_data)

        except sql3.Error as exc:
            raise DatabaseExecutionError(exc)

        finally:
            cursor.close()

    async def get_visits(self, patient_id: int) -> list[Visit]:
        pass

    async def commit(self) -> None:
        self.connection.commit() 

