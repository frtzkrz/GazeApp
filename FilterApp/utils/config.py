from pathlib import Path
import plotly.express as px

ROI_NAMES: list[str] = ['Cornea', 'CiliaryBody', 'Iris', 'Lens', 'Macula', 'OpticalDisc', 'Retina', 'OpticalNerve']
PATIENT_ID = "P23336"

H5_PATH = Path(f"data/{PATIENT_ID}_9_angles.h5")

N_WEIGHTS = 10

MARGIN_TOP = 30
MARGIN_SIDE = 40

NUM_POINTS_DVH = 200

COLOR_SCALE = px.colors.sequential.Viridis

EPS_FILTER = 0

ESPENSEN_METRICS = {'Cornea': {"type": "D", "value": 20}, 'CiliaryBody': {"type": "V", "value": 27}, 'Lens': {"type": "D", "value": 5}, 'Macula': {"type": "D", "value": 2}, 'OpticalDisc': {"type": "D", "value": 20}, 'Retina': {"type": "V", "value": 55}, 'OpticalNerve': {"type": None, "value": None}, 'Iris': {"type": None, "value": None}}

#{"type": , "value": }


PASSIVE_OPACITY = 0.2
ACTIVE_OPACITY = 0.6
METRIC_OPACITY = 0.5


METRIC_TYPES = ["D", "V"]
