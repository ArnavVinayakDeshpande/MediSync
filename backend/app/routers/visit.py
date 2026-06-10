"""
"""

from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Body

from app.models.visit import Visit
import app.models.visit_manager as vm


router = APIRouter(
        prefix = "/visits",
        tags = ["Visits"]
        )

# Create
def create():
    pass

def delete():
    pass

def deleteall():
    pass

def getid():
    pass

def get():
    pass

def getall():
    pass

def update():
    pass

