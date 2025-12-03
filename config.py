#SET UP

import matplotlib.pyplot as plt

from GazeOptimizer.patient_functions.patient import *

from itertools import cycle
import h5py
import pickle

PATIENT_ID = 'P23336'
H5_FILE_PATH = f'data/{PATIENT_ID}/{PATIENT_ID}_9_angles.h5'

PICKLE_PATH = f"data/pickles/{PATIENT_ID}_9_combo.dat"

ROI_NAMES = ['Cornea', 'CiliaryBody', 'Iris', 'Lens', 'Macula', 'OpticalDisc', 'Retina', 'OpticalNerve']
N_PLOTS = len(ROI_NAMES)

N_POINTS = 100 #points on dvh plots

ESPENSEN_METRICS = {
    "Cornea": ("D", 20, None),
    "CiliaryBody": ("V", 27, None),
    "Iris": (None, None, None),
    "Lens": ("D", 5, None),
    "Macula": ("D", 2, None),
    "OpticalDisc": ("D", 20, None),
    "Retina": ("V", 55, None),
    "OpticalNerve": (None, None, None),
}


#Plotting stuff
FIGSIZE_X = 950
FIGSIZE_Y = 420
CMAP = plt.cm.viridis
EPS = 0.5

TWO_BEAMS=True

COLORS = [
    ("#e41a1c", "red"),
    ("#ff7f00", "orange"),
    ("#f781bf", "pink"),
    ("#000000", "black"),
]
COLORS = [c[0] for c in COLORS]
# If you only need a list of hex values:
HIGHLIGHT_COLORS = cycle(COLORS)


PATIENT = Patient(patient_id=PATIENT_ID, h5_file_path=H5_FILE_PATH)
with h5py.File(PATIENT.h5_file_path, "r") as h5_file:
    PLANS_1_BEAM = [TreatmentPlan(PATIENT, angle_key=angle_key, dose=h5_file[angle_key][:]) for angle_key in PATIENT.gaze_angle_keys]

def load_data():
    try:
        with open(PICKLE_PATH) as f:
            plans_2_beam = pickle.load(f)
        print("loaded")
    except:
        plans_2_beam = []
    return plans_2_beam

def save_data(data):
    with open(PICKLE_PATH, "wb") as f:
        pickle.dump(data, f)
        print('saved')




def find_all_gaze_combos(n_steps=3):
    print("Calculating Combos")
    plans = []
    with h5py.File(PATIENT.h5_file_path, "r") as h5_file:
        for i, gaze_angle_key_1 in enumerate(PATIENT.gaze_angle_keys):

            #Load dose 1
            dose_1 = h5_file[gaze_angle_key_1][:]

            #Add single beam dose
            plans.append(TreatmentPlan(
                patient=PATIENT, 
                angle_key=gaze_angle_key_1, 
                dose=dose_1)
            )
            
            
            for gaze_angle_key_2 in PATIENT.gaze_angle_keys[i+1:]:
                dose_2 = h5_file[gaze_angle_key_2][:]

                #add all two beam plans
                for w in np.linspace(0, 1, n_steps, endpoint=False)[1:]:
                    combined_dose = w*dose_1 + (1-w)*dose_2
                    p = TreatmentPlan(
                        patient=PATIENT,
                        angle_key=gaze_angle_key_1,
                        angle_key_2=gaze_angle_key_2,
                        dose=combined_dose,
                        beam_weight=w
                    )
                    plans.append(p)
    print("Finished")
    print(len(plans))
    return plans

if TWO_BEAMS: 
    plans_2_beam = load_data()
    if plans_2_beam == []:
        plans_2_beam = find_all_gaze_combos(n_steps=10)
        save_data(plans_2_beam)
    ALL_PLANS = plans_2_beam


else: ALL_PLANS = PLANS_1_BEAM
