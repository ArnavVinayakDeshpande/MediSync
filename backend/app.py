"""
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleWare

from database.database import database
from managers.patient_manager import patient_manager


def main():
    # Create the fastapi app
    app = FastAPI(title="MediSync Backend")

    app.app_middleware(CORSMiddleWare,
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

    # Create database
    database = Database("")

    # Create patient manager
    patient_manager = PatientManager(database)

if __name__ == "__main__":
    main()

