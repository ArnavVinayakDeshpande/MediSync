"""
"""

from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Body
from fastapi import Query

import app.managers.visit_manager as vm
import app.managers.patient_manager as pm
from app.managers.exceptions import *
from app.models.visit import Visit
from app.common.converter import *


router = APIRouter(
        prefix = "/visits",
        tags = ["Visits"]
)

# Create
@router.post("")
def create(data: dict = Body(...)):
    if pm.patient_manager is None:
        raise HTTPException(
            status_code = 500,
            detail = "Patient manager has not been initialized, Visit Manager needs Patient Manager to be initialized."
        )

    if vm.visit_manager is None:
        raise HTTPException(
            status_code = 500,
            detail = "Visit Manager has not been initialized."
        )

    try:
        created_id = vm.visit_manager.create(
            patient_id = data["patient_id"],
            visit = visit_from_json_fmt(data)
        )
        
        patient_name = pm.patient_manager.get_name(data["patient_id"])

        # Patient name will definitely be not None, since if patient does not exist then 
        # visit_manager will throw exception

        return {
            "sucess": True,
            "visit_id": created_id,
            "patient_name": patient_name
        }

    except VMDuplicateEntryError as exc:
        raise HTTPException(
            status_code = 409,
            detail = str(exc)
        ) from exc

    except VMInvalidInputsError as exc:
        raise HTTPException(
            status_code = 400,
            detail = str(exc)
        ) from exc

    except VMDatabaseError as exc:
        raise HTTPException(
            status_code = 500,
            detail = str(exc)
        ) from exc

    except (KeyError, ValueError) as exc:
        raise HTTPException(
            status_code = 400,
            detail = "Malformed request body."
        ) from exc

@router.delete("/{visit_id}")
def delete(visit_id: str):
    if vm.visit_manager is None:
        raise HTTPException(
            status_code = 500,
            detail = "Visit Manager has not been initialized."
        )

    try:
        vm.visit_manager.delete(visit_id)

        return {
            "success": True
        }

    except VMAbsentEntryError as exc:
        raise HTTPException(
            status_code = 404,
            detail = str(exc)
        ) from exc

    except VMDatabaseError as exc:
        raise HTTPException(
            status_code = 500,
            detail = str(exc)
        ) from exc

@router.delete("")
def deleteall(patient_id: str = Query()):
    if vm.visit_manager is None:
        raise HTTPException(
            status_code = 500,
            detail = "Visit Manager has not been initialized."
        )

    try:
        vm.visit_manager.deleteall(patient_id)

        return {
            "success": True
        }

    except VMDatabaseError as exc:
        raise HTTPException(
            status_code = 500,
            detail = str(exc)
        ) from exc

@router.get("/id")
def getid():
    if vm.visit_manager is None:
        raise HTTPException(
            status_code = 500,
            detail = "Visit Manager has not been initialized."
        )

    try:
        return vm.visit_manager.create_id()

    except VMDatabaseError as exc:
        raise HTTPException(
            status_code = 500,
            detail = str(exc)
        ) from exc

@router.get("/{visit_id}")
def get(visit_id: str):
    if vm.visit_manager is None:
        raise HTTPException(
            status_code = 500,
            detail = "Visit Manager has not been initialized."
        )

    if pm.patient_manager is None:
        raise HTTPException(
            status_code = 500,
            detail = "Patient Manager has not been initialized."
        )

    try:
        data = vm.visit_manager.get(visit_id)

        if data is None:
            raise HTTPException(
                status_code = 404,
                detail = "The requested visit does not exist."
            )

        patient_name = pm.patient_manager.get_name(data.patient_id)

        if patient_name is None:
            raise HTTPException(
                status_code = 500,
                detail = "Issue detected! Internal database might be corrupted."
            )

        return visit_to_json_fmt(
            visit = data.visit,
            patient_id = data.patient_id,
            patient_name = patient_name
        )

    except VMDatabaseError as exc:
        raise HTTPException(
            status_code = 500,
            detail = str(exc)
        ) from exc

@router.get("")
def getall(
    patient_id: str | None = Query(default = None),
    size: int | None = Query(default = None),
    offset: int | None = Query(default = None),
    fees_pending: bool | None = Query(default = None),
    follow_up: bool | None = Query(default = None)
):
    if vm.visit_manager is None:
        raise HTTPException(
            status_code = 500,
            detail = "Visit Manager has not been initialized."
        )

    if pm.patient_manager is None:
        raise HTTPException(
            status_code = 500,
            detail = "Patient Manager has not been initialized."
        )

    try:
        data = vm.visit_manager.getall(
            patient_id,
            size,
            offset,
            fees_pending,
            follow_up
        )

        patient_names = [
            pm.patient_manager.get_name(visit.patient_id) for visit in data
        ]

        if any(patient_name is None for patient_name in patient_names):
            raise HTTPException(
                status_code = 500,
                detail = "Issue Detected! Internal database might be corrupted."
            )

        return [
            visit_to_json_fmt(
                visit = data[i].visit,
                patient_id = data[i].patient_id,
                patient_name = patient_names[i] # pyright: ignore[reportArgumentType] (for pyright)
            ) for i in range(len(data))
        ]

    except VMDatabaseError as exc:
        raise HTTPException(
            status_code = 500,
            detail = str(exc)
        ) from exc

@router.patch("/{visit_id}")
def update(visit_id: str, data: dict = Body(...)):
    if vm.visit_manager is None:
        raise HTTPException(
            status_code = 500,
            detail = "Visit Manager has not been initialized."
        )

    try:
        visit = visit_from_json_fmt(data)

        if visit.id != visit_id:
            exc = VMInvalidInputsError()
            raise HTTPException(
                status_code = 400,
                detail = str(exc)
            ) from exc

        vm.visit_manager.update(
            visit_id = visit_id,
            date = visit.date,
            diagnosis = visit.diagnosis,
            prescription = visit.prescription,
            notes = visit.notes,
            fees_paid = visit.fees_paid,
            fees_pending = visit.fees_pending,
            follow_up_date = visit.follow_up_date
        )

        return {
            "success": True
        }

    except VMAbsentEntryError as exc:
        raise HTTPException(
            status_code = 404,
            detail = str(exc)
        ) from exc

    except VMInvalidInputsError as exc:
        raise HTTPException(
            status_code = 400,
            detail = str(exc)
        ) from exc

    except VMDatabaseError as exc:
        raise HTTPException(
            status_code = 500,
            detail = str(exc)
        ) from exc

    except (KeyError, ValueError) as exc:
        raise HTTPException(
            status_code = 400,
            detail = "Malformed request body."
        ) from exc

