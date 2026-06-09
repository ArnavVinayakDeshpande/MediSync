"""
"""

from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Body

from app.managers.patient_manager import patient_manager
from app.managers.exceptions import *
from app.models.patient import *
from app.models.visit import *
from app.models.medical_condition import *
from app.common.converter import *


router = APIRouter(
        prefix = "/patients",
        tags = ["Patients"]
        )

# Create
@router.post("")
def create(data: dict = Body(...)):
    if not patient_manager:
        raise HTTPException(
                status_code = 500,
                detail = "Could not access internal database."
                )

    try:
        created_id = patient_manager.create(
                name = data["name"],
                dob = date_from_json_fmt(data["dob"]),
                number = data["number"],
                condition = data["condition"],
                is_active = data["is_active"]
                ) 

        return {"patient_id": created_id, "success": True}

    except PMDatabaseError:
        raise HTTPException(
                status_code = 500,
                detail = "Could not access internal database."
                )

    except PMDuplicateEntryError:
        raise HTTPException(
                status_code = 409,
                detail = "Patient with same ID / number already exists."
                )

    except (KeyError, ValueError, PMInvalidInputsError):
        raise HTTPException(
                status_code = 400,
                detail = "Invalid input format for data."
                )

@router.delete("/{patient_id}")
def delete(patient_id: int):
    if not patient_manager:
        raise HTTPException(
                status_code = 500,
                detail = "Could not access internal database."
                )

    try:
        patient_manager.delete(patient_id) 

    except PMDatabaseError:
        raise HTTPException(
                status_code = 500,
                detail = "Could not access internal database."
                )

    except PMAbsentEntryError:
        raise HTTPException(
                status_code = 404,
                detail = "Could not find the patient with the given id."
                )

@router.get("/{patient_id}")
def get(patient_id: int):
    if not patient_manager:
        raise HTTPException(
                status_code = 500,
                detail = "Could not access internal database."
                )

    try:
        data = patient_manager.get(patient_id)

        if data:
            return patient_to_json_fmt(data)

        raise HTTPException(
                status_code=404,
                detail = "Could not find the patient with the given id."
                )

    except PMDatabaseError as exc:
        raise HTTPException(
                status_code=500,
                detail = "Could not access internal database."
                )

@router.get("")
def getall():
    if not patient_manager:
        raise HTTPException(
                status_code = 500,
                detail = "Could not access internal database."
                )

    try:
        data = patient_manager.getall()

        if data:
            return [patient_to_json_fmt(d) for d in data]

        return []
    
    except PMDatabaseError:
        raise HTTPException(
                status_code = 500,
                detail = "Could not access internal database."
                )

@router.get("/id")
def getid():
    if not patient_manager:
        raise HTTPException(
                status_code = 500,
                detail = "Could not access internal database."
                )

    try:
        id = patient_manager.create_id()

        return id

    except PMDatabaseError:
        raise HTTPException(
                status_code = 500,
                detail = "Could not access internal database."
                )

@router.patch("/{patient_id}")
def update(patient_id: int, data:dict = Body(...)):
    if not patient_manager:
        raise HTTPException(
                status_code = 500,
                detail = "Could not acess internal database."
                )

    try:
        pass

    except PMDatabaseError:
        raise HTTPException(
                status_code = 500,
                detail = "Could not access internal database."
                )

