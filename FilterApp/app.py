from data.h5_loader import load_data
from utils.config import *
from components.layout import create_layout
from dash import Dash, html, dcc, callback_context

from dash_bootstrap_components.themes import BOOTSTRAP

import dash

from dash.dependencies import Input, Output, State, MATCH, ALL
import plotly.graph_objs as go



def main() -> None:
    #load patient and plans
    patient = load_data(
        path=H5_PATH, 
        patient_id=PATIENT_ID, 
        two_beam=True, 
        n_weights=N_WEIGHTS
    )

    app = dash.Dash(
        external_stylesheets=[BOOTSTRAP],
    )
    
    app.title = "GazeApp"

    app.layout = create_layout(app=app, patient=patient)

    app.run(debug=True, use_reloader=True)

if __name__ == "__main__":
    main()
    