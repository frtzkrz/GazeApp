from models.patient import Patient
from utils.config import *  


def update_active_plans(patient: Patient, all_filters: dict[str, list[int]]) -> None:
    print("update plans")
    patient.active_plans = [plan for plan in patient.plans if plan.apply_filters(filters=all_filters)]