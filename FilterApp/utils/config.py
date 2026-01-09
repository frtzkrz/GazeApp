from pathlib import Path
import plotly.express as px
from itertools import cycle

################################################
#-----------------------------------------------
#Probably you want to change these parameters:
PATIENT_ID = "P23336"
#PATIENT_ID = "23129"
#PATIENT_ID = "17213"

H5_PATH = Path(f"data/{PATIENT_ID}_9_angles.h5")

N_WEIGHTS = 10

TWO_BEAMS = True

#-----------------------------------------------
################################################






ROI_NAMES: list[str] = ['Cornea', 'CiliaryBody', 'Iris', 'Lens', 'Macula', 'OpticalDisc', 'Retina', 'OpticalNerve']

MARGIN_TOP = 30
MARGIN_SIDE = 40

NUM_POINTS_DVH = 200

COLOR_SCALE = px.colors.sequential.Viridis

EPS_FILTER = 0

ESPENSEN_METRICS = {'Cornea': {"type": "D", "value": 20}, 'CiliaryBody': {"type": "V", "value": 27}, 'Lens': {"type": "D", "value": 5}, 'Macula': {"type": "D", "value": 2}, 'OpticalDisc': {"type": "D", "value": 20}, 'Retina': {"type": "V", "value": 55}, 'OpticalNerve': {"type": None, "value": None}, 'Iris': {"type": None, "value": None}}

STARTING_METRICS = ESPENSEN_METRICS


PASSIVE_OPACITY = 0.2
ACTIVE_OPACITY = 0.7
METRIC_OPACITY = 1.


METRIC_TYPES = ["D", "V"]


HIGHLIGHT_OPACITY = 1.

HIGHLIGHT_LINE_WIDTH = 3

HIGHLIGHT_COLORS = [
    ("#e41a1c", "red"),
    ("#ff7f00", "orange"),
    ("#f781bf", "pink"),
    ("#000000", "black"),
]
# If you only need a list of hex values:
HIGHLIGHT_COLORS = cycle([c[0] for c in HIGHLIGHT_COLORS])