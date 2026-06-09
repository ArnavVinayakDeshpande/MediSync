"""
"""

import os
import pathlib
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database.database import database
from .managers.patient_manager import patient_manager
from .routers.patient import router as patient_router


app = None

def get_db_path() -> pathlib.Path:
    curr_dir = Path(__file__).parent

    wd = curr_dir.parent

    db = curr_dir / "data" / "lenest_database.db"


def main():
    global app

    # Create the fastapi app
    app = FastAPI(title="MediSync Backend")

    app.app_middleware(CORSMiddleware,
                       allow_origins=[
                           ""
                           ],
                       allow_credentials=True,
                       allow_methods=[
                            "*"
                           ],
                       allow_headers=[
                           "*"
                           ]
                       )

    # Include the routers
    app.include_router(patient_router)

    # Create database
    database = Database(get_db_path())

    # Create patient manager
    patient_manager = PatientManager(database)

if __name__ == "__main__":
    main()

