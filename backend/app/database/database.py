"""
"""

from pymongo.database import Database as MongoDB

from app.database.exceptions import *
from app.database.patient_repo import PatientRepository
from app.database.visit_repo import VisitRepository 
from app.database.wa_msg_history_repo import WhatsAppMsgHistoryRepository
from app.database.wa_template_repo import WhatsAppTemplateRepository
from app.database.client import MongoDBClient


class Database:
    def __init__(self, client: MongoDBClient) -> None:
        self._client = client

        self._hospital_database = client.get_database("hospital_db")
        self._whatsapp_database = client.get_database("whatsapp_db")

        self._patient_repository = PatientRepository(self._hospital_database["patients"])
        self._visit_repository = VisitRepository(self._hospital_database["visits"])

    @property
    def hospital_db(self) -> MongoDB:
        return self._hospital_database

    @property
    def whatsapp_db(self) -> MongoDB:
        return self._whatsapp_database

    @property
    def patient_repository(self) -> PatientRepository:
        return self._patient_repository

database: Database | None = None

