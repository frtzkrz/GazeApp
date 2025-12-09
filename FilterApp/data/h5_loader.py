import h5py
from models.patient import Patient
from utils.config import *
from pathlib import Path

def load_data(
        path: Path, 
        patient_id: str, 
        two_beam: bool = False, 
        n_weights: int = 1
    ) -> Patient:
    """
    Loads data from h5 file and calculates plans
    
    :param path: path to h5 file
    :type path: Path
    :param patient_id: patient_id
    :type patient_id: str
    :param two_beam: if two beam plans have to be generated. Default: False
    :type two_beam: bool
    :param n_weights: how many equal spaced weights should be chosen. Default: 1, so only equal weighting
    :type n_weights: int
    """
    with h5py.File(name=path, mode='r') as h5_file:
        patient = Patient(
            patient_id=patient_id,
            h5_file=h5_file
        )
        patient.add_plans(h5_file=h5_file, two_beam=two_beam, n_weights=n_weights)
    
    return patient