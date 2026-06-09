"""
"""

import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.database import database, Database
from app.managers.patient_manager import PatientManager
import app.managers.patient_manager as patient_manager
from .routers.patient import router as patient_router


def get_db_path() -> Path:
    path = Path(__file__).parent.parent.parent / "data"

    db = path / "lenest_database.db"

    return db

print(get_db_path())

app = FastAPI(title = "MediSync Backend")

app.add_middleware(
        CORSMiddleware,
        allow_origins = [""],
        allow_credentials = True,
        allow_methods = ["*"],
        allow_headers = ["*"]
        )

app.include_router(patient_router)

database = Database(get_db_path())
patient_manager.patient_manager = PatientManager(database)

@app.get("/")
def root():
    return {"status": "MediSync backend is running"}


