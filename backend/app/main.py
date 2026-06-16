"""
"""

import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.database import Database
import app.database.database as db
from app.managers.patient_manager import PatientManager
import app.managers.patient_manager as patient_manager
from app.managers.visit_manager import VisitManager
import app.managers.visit_manager as visit_manager
from app.routers.patient import router as patient_router
from app.routers.visit import router as visit_router


def get_db_path() -> Path:
    path = Path(__file__).parent.parent.parent / "data"

    db = path / "lenest_database.db"

    return db

print(get_db_path())

app = FastAPI(title = "MediSync Backend")

app.add_middleware(
        CORSMiddleware,
        allow_origins = ["http://localhost:5173/"],
        allow_credentials = True,
        allow_methods = ["*"],
        allow_headers = ["*"]
        )

app.include_router(patient_router)
app.include_router(visit_router)

db.database = Database(get_db_path())
patient_manager.patient_manager = PatientManager(db.database)
visit_manager.visit_manager = VisitManager(db.database)

@app.get("/")
def root():
    return {"status": "MediSync backend is running"}


