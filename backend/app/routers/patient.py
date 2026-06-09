"""
"""

from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Body

import app.managers.patient_manager as pm

from app.managers.exceptions import *
from app.models.patient import *
from app.models.visit import *
from app.models.medical_condition import *
from app.common.converter import *


router = APIRouter(
        prefix="/patients",
        tags=["Patients"]
        )

# Create
@router.post("")
def create(data: dict = Body(...)):
    if pm.patient_manager is None:
        raise HTTPException(
                status_code=500,
                detail="Patient manager is not initialized."
                )

    try:
        created_id = pm.patient_manager.create(
                patient_from_json_fmt(data)
                )

        return {
                "patient_id": created_id,
                "success": True
                }

    except PMDuplicateEntryError as exc:
        raise HTTPException(
                status_code=409,
                detail=str(exc)
                ) from exc

    except PMInvalidInputsError as exc:
        raise HTTPException(
                status_code=400,
                detail=str(exc)
                ) from exc

    except PMDatabaseError as exc:
        raise HTTPException(
                status_code=500,
                detail=str(exc)
                ) from exc

    except (KeyError, ValueError) as exc:
        raise HTTPException(
                status_code=400,
                detail="Malformed request body."
                ) from exc


# Delete
@router.delete("/{patient_id}")
def delete(patient_id: str):
    if pm.patient_manager is None:
        raise HTTPException(
                status_code=500,
                detail="Patient manager is not initialized."
                )

    try:
        pm.patient_manager.delete(patient_id)

        return {"success": True}

    except PMAbsentEntryError as exc:
        raise HTTPException(
                status_code=404,
                detail=str(exc)
                ) from exc

    except PMDatabaseError as exc:
        raise HTTPException(
                status_code=500,
                detail=str(exc)
                ) from exc


# Reserve / create ID
@router.get("/id")
def getid():
    if pm.patient_manager is None:
        raise HTTPException(
                status_code=500,
                detail="Patient manager is not initialized."
                )

    try:
        return pm.patient_manager.create_id()

    except PMDatabaseError as exc:
        raise HTTPException(
                status_code=500,
                detail=str(exc)
                ) from exc


# Get single patient
@router.get("/{patient_id}")
def get(patient_id: str):
    if pm.patient_manager is None:
        raise HTTPException(
                status_code=500,
                detail="Patient manager is not initialized."
                )

    try:
        data = pm.patient_manager.get(patient_id)

        if data is None:
            raise HTTPException(
                    status_code=404,
                    detail="The requested patient does not exist."
                    )

        return patient_to_json_fmt(data)

    except PMDatabaseError as exc:
        raise HTTPException(
                status_code=500,
                detail=str(exc)
                ) from exc


# Get all patients
@router.get("")
def getall():
    if pm.patient_manager is None:
        raise HTTPException(
                status_code=500,
                detail="Patient manager is not initialized."
                )

    try:
        data = pm.patient_manager.getall()

        if data:
            return [patient_to_json_fmt(d) for d in data]

        return []

    except PMDatabaseError as exc:
        raise HTTPException(
                status_code=500,
                detail=str(exc)
                ) from exc


# Update
@router.patch("/{patient_id}")
def update(patient_id: str, data: dict = Body(...)):
    if pm.patient_manager is None:
        raise HTTPException(
                status_code=500,
                detail="Patient manager is not initialized."
                )

    try:
        pm.patient_manager.update(
                patient_id=patient_id,
                name=data.get("name"),
                dob=(
                    date_from_json_fmt(data["dob"])
                    if "dob" in data else None
                ),
                number=data.get("number"),
                condition=data.get("condition"),
                is_active=data.get("is_active")
                )

        return {"success": True}

    except PMAbsentEntryError as exc:
        raise HTTPException(
                status_code=404,
                detail=str(exc)
                ) from exc

    except PMInvalidInputsError as exc:
        raise HTTPException(
                status_code=400,
                detail=str(exc)
                ) from exc

    except PMDatabaseError as exc:
        raise HTTPException(
                status_code=500,
                detail=str(exc)
                ) from exc

    except (KeyError, ValueError) as exc:
        raise HTTPException(
                status_code=400,
                detail="Malformed request body."
                ) from exc

