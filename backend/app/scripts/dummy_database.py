"""
Populate the local database with dummy patients.

Usage:
    python populate_database.py
"""

import random
from datetime import date, timedelta
from pathlib import Path

from app.models.patient import Patient
from app.models.medical_condition import MedicalCondition
from app.models.visit import Visit
from app.database.database import Database
from app.managers.patient_manager import PatientManager
from app.managers.visit_manager import VisitManager


FIRST_NAMES = [
    "Aarav", "Vivaan", "Aditya", "Arjun", "Vihaan",
    "Krishna", "Ishaan", "Rohan", "Rahul", "Karan",
    "Amit", "Akash", "Aniket", "Harsh", "Dhruv",
    "Yash", "Parth", "Om", "Nikhil", "Siddharth",
    "Aryan", "Shivam", "Tanmay", "Atharva", "Vedant",
    "Sneha", "Priya", "Riya", "Ananya", "Anjali",
    "Pooja", "Aditi", "Kavya", "Neha", "Ishita",
    "Shruti", "Diya", "Meera", "Khushi", "Nisha",
    "Sakshi", "Avni", "Riddhi", "Vaishnavi", "Simran",
    "Palak", "Rutuja", "Shreya", "Mansi", "Prachi"
]

LAST_NAMES = [
    "Sharma", "Patel", "Singh", "Verma", "Gupta",
    "Deshmukh", "Kulkarni", "Joshi", "Nair", "Iyer",
    "Reddy", "Rao", "Mehta", "Jain", "Chopra",
    "Malhotra", "Kapoor", "Khan", "Shaikh", "Ansari",
    "Yadav", "Tiwari", "Pandey", "Pawar", "Patil",
    "Chavan", "Sawant", "Bhosale", "More", "Jadhav",
    "Mishra", "Das", "Roy", "Banerjee", "Mukherjee",
    "Saxena", "Agarwal", "Mahajan", "Dubey", "Shukla"
]

AREAS = [
    "Shivajinagar",
    "Kothrud",
    "Baner",
    "Hadapsar",
    "Wakad",
    "Aundh",
    "Karve Nagar",
    "Pimpri",
    "Nigdi",
    "Kharadi",
]

CONDITIONS = list(MedicalCondition)

def random_dob() -> date:
    today = date.today()

    # Age between 1 and 90
    age_days = random.randint(365, 90 * 365)

    return today - timedelta(days=age_days)

def random_phone() -> str:
    return "".join(random.choice("0123456789") for _ in range(10))

def random_address() -> str:
    return (
        f"House {random.randint(1, 999)}, "
        f"{random.choice(AREAS)}, Pune"
    )


def create_dummy_patient(pid: str) -> Patient:
    return Patient(
        id = pid,                     # Let manager generate
        name = f"{random.choice(FIRST_NAMES)} "
             f"{random.choice(LAST_NAMES)}",
        dob = random_dob(),
        number = random_phone(),
        condition = random.choice(CONDITIONS),
        is_active = random.choice([True, False]),
    )


def main():
    database_path = Path(__file__).parent.parent.parent.parent / "data" / "lenest_database.db"
    print(f"Creating a database: {database_path}")
    database = Database(database_path)
    manager = PatientManager(database)

    for _ in range(1000):
        patient = create_dummy_patient(manager.create_id())
        manager.create(patient)


if __name__ == "__main__":
    main()

