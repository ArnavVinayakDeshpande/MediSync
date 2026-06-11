"""
"""

from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Body
from fastapi import Query

from app.models.visit import Visit
import app.managers.visit_manager as vm
from app.common.converter import *


router = APIRouter(
        prefix = "/visits",
        tags = ["Visits"]
        )

# Create
@router.post("")
def create(data: dict = Body(...)):
    if vm.visit_manager is None:
        raise HTTPException(
                status_code = 500,
                detail = "Visit Manager has not been initialized."
                )

    try:
        created_id = vm.visit_manager.create(
                visit_from_json_fmt(data)
                )

        return {
                "visit_id": created_id,
                "sucess": True
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

        return {"success": True}

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

        return {"success": True}

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

    try:
        data = vm.visit_manager.get(visit_id)

        if data is None:
            raise HTTPException(
                    status_code = 404,
                    detail = "The requested visit does not exist."
                    )

        return visit_to_json_fmt(data)

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

    try:
        data = vm.visit_manager.getall(
                patient_id,
                size,
                offset,
                fees_pending,
                follow_up
                )

        return [visit_to_json_fmt(d) for d in data]

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

        return {"success": True}

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

