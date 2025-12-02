#SET UP

import matplotlib.pyplot as plt
from GazeOptimizer.patient_functions.patient import *

from itertools import cycle
import h5py
import pickle

PATIENT_ID = 'P23336'
H5_FILE_PATH = f'data/{PATIENT_ID}/{PATIENT_ID}_delta_15.h5'

PICKLE_PATH = f"data/pickles/{PATIENT_ID}_9_combo.dat"

ROI_NAMES = ['Cornea', 'CiliaryBody', 'Iris', 'Lens', 'Macula', 'OpticalDisc', 'Retina', 'OpticalNerve']
N_PLOTS = len(ROI_NAMES)

N_POINTS = 100 #points on dvh plots

#Plotting stuff
FIGSIZE_X = 950
FIGSIZE_Y = 420
CMAP = plt.cm.viridis
EPS = 2

TWO_BEAMS=False

COLORS = [
    ("#e41a1c", "red"),
    ("#ff7f00", "orange"),
    ("#f781bf", "pink"),
    ("#000000", "black"),
]
COLORS = [c[0] for c in COLORS]
# If you only need a list of hex values:
HIGHLIGHT_COLORS = cycle(COLORS)


pat = Patient(patient_id=PATIENT_ID, h5_file_path=H5_FILE_PATH)
with h5py.File(pat.h5_file_path, "r") as h5_file:
    PLANS_1_BEAM = [TreatmentPlan(pat, angle_key=angle_key, dose=h5_file[angle_key][:]) for angle_key in pat.gaze_angle_keys]

def load_data():
    try:
        with open(PICKLE_PATH) as f:
            weights, plans_2_beam = pickle.load(f)
    except:
        weights, plans_2_beam = [], []
    return weights, plans_2_beam

def save_data(data):
    with open(PICKLE_PATH, "wb") as f:
        pickle.dump(data, f)
        print('saved')



if TWO_BEAMS: 
    weights, plans_2_beam = load_data()
    if weights == []:
        weights, _, plans_2_beam = calculate_gaze_combos(patient=pat)
        save_data([weights, plans_2_beam])


ALL_PLANS = PLANS_1_BEAM