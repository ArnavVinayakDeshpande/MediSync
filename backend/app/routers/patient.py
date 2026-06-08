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
        prefix="/patients",
        tags=["Patients"]
        )

# Add
@router.post("")
def add_patient(data: Body(...)):
    if patient_manager is None:
        raise HTTPException(status_code=500,
                            detail="Could not access internal database.")

    try:
        patient_manager.create_patient_metadata(name=data["name"],
                                                dob=date_from_json_fmt(data["dob"]),
                                                number=data["number"],
                                                condition=MedicalCondition(data["condition"]),
                                                is_active=data["is_active"]
                                                )

    except KeyError, PMInvalidInputsError:
        raise HTTPException(status_code=400,
                            detail="Information given in an invalid format.")

    except PMDatabaseError:
        raise HTTPException(status_code=500,
                            detail="Could not access internal database.")

    except PMDuplicateEntryError:
        raise HTTPException(status_code=409,
                            detail="Given patient with id/number already exists.")

    return {"success": True}

@router.delete("/{patient_id}")
def delete_patient(patient_id: int):
    if patient_manager is None:
        raise HTTPException(status_code=500,
                            detail="Could not access internal database.")

    try:
        patient_manager.delete(patient_id)

    except PMDatabaseError:
        raise HTTPException(status_code=500,
                            detail="Could not access internal database.")

    except PMAbsentEntryError:
        raise HTTPException(status_code=404,
                            detail="Could not find the patient requested.")

    return {"success": True}

@router.patch("/{patient_id}")
def patch_patient(patient_id: int):
    pass

@router.get("/{patient_id}")
def get_patient(patient_id: int):
    if patient_manager is None:
        raise HTTPException(status_code=500,
                            detail="Could not access internal database.")

    try:
        data = patient_manager.get_patient_metadata(patient_id)

        if data is None:
            raise HTTPException(status_code=404,
                                detail="Could not find the patient requested.")
        
        return patient_metadata_to_json_fmt(patient_id, data)

    except PMDatabaseError:
        raise HTTPException(status_code=500,
                            detail="Could not access internal database.")

@router.get("")
def get_all_patients():
    if patient_manager is None:
        raise HTTPException(status_code=500,
                            detail="Could not access internal database.")

