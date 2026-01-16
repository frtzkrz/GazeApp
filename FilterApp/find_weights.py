from models.patient import Patient
import h5py
from utils.config import ESPENSEN_METRICS, ROI_NAMES



def load_patient(patient_id, h5_path) -> Patient:
    with h5py.File(h5_path, 'r') as h5_file:
        patient = Patient(patient_id=patient_id, h5_file=h5_file)
        patient.add_plans(h5_file=h5_file, two_beam=False, n_weights=1)
    for plan in patient.plans:
        for roi in ROI_NAMES:
            plan.dvhs[roi].update_metric(metric=ESPENSEN_METRICS[roi])

    return patient



if __name__ == "__main__":
    patient = load_patient(patient_id='17213', h5_path='data/17213_9_angles.h5')
    best_plan_name = '(0, 0)'
    best_plan = patient.plans
