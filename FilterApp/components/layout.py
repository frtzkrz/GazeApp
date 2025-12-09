from dash import Dash, html, Input, Output, ALL, MATCH, Patch, dcc
from . import figures
from models.patient import Patient
from utils.config import *
from components.hide_lines import hide_lines_patch
from . import ids


def create_layout(app: Dash, patient: Patient) -> html.Div:
    return figures.render(app=app, patient=patient)