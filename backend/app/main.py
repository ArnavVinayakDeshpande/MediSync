"""
"""

from os import getenv
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.client import MongoDBClient
import app.database.database as DB
import app.managers.patient_manager as PM
import app.managers.visit_manager as VM
from app.routers.patient import router as patient_router
from app.routers.visit import router as visit_router


# Load the enviroment variables
load_dotenv() 

# Create and configure FastAPI app
app = FastAPI(title = "MediSync Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins = [
        "http://localhost:5173/"
    ],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"]
)

app.include_router(patient_router)
app.include_router(visit_router)

# Create the MongoDB client
# Get the username and password variables
mongodb_username = getenv("MONGODB_USERNAME")
mongodb_password = getenv("MONGODB_PASSWORD")

if not mongodb_username or not mongodb_password:
    raise Exception("initialization: environment does not have MONGODB_USERNAME and MONGODB_PASSWORD variables")

mongodb_client = MongoDBClient(
    username = mongodb_username,
    password = mongodb_password
)

# Create the database connection
DB.database = DB.Database(mongodb_client)

# Create the patient manager
PM.patient_manager = PM.PatientManager(DB.database)

# Create the visit manager
VM.visit_manager = VM.VisitManager(DB.database)

# Any functions

@app.get("/")
def root():
    return {
        "status": "MediSync backend is running" 
    }

@app.get("/help/list-urls")
def help_list_urls():
    return {
        "data": [
            {
                "url": "/patients",
                "desc": "Access any patient specific data via this url."
            },
            {
                "url": "/visits",
                "desc": "Access any visit specific data via this url."
            }
        ]
    }

