from dash import Dash, dcc, Output, Input, ALL, State, Patch, callback_context
from models.patient import Patient
import plotly.graph_objs as go
from . import ids
from utils.config import *
import numpy as np

from components.dvh_plot_helpers import create_dvh_plot, update_dvh_plots

def render(app: Dash, patient: Patient, roi: str) -> dcc.Graph:
    @app.callback(
        Output(component_id={"type": ids.DVH_PLOT, "index": roi}, component_property="figure"),
        Input(component_id=ids.FILTERS, component_property="data"),
        Input(component_id=ids.METRICS, component_property="data"),
        Input(component_id=ids.HIGHLIGHT_IDXS, component_property="data"),
        prevent_initial_callback=False
    )

    #Update plans and colors
    def update(all_filters: dict[str, list[int]], all_metrics: dict[str, dict], highlight_idxs: list[int]) -> Patch:
        ctx = callback_context
        patch = Patch()
        return update_dvh_plots(
            patient=patient, 
            roi=roi, 
            patch=patch, 
            ctx=ctx, 
            all_filters=all_filters, 
            all_metrics=all_metrics,
            highlight_idxs=highlight_idxs
        )
    
    return create_dvh_plot(patient=patient, roi=roi)