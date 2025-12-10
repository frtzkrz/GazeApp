from __future__ import annotations

from dash import Dash, dcc, html, Input, State, Output, Patch
import plotly.graph_objs as go
from . import ids
from utils.config import *
import plotly.express as px


from models.patient import Patient
from components.gaze_scatter_helpers import update_scatter, plot_active_scatter


def render(app: Dash, patient: Patient, roi: str) -> dcc.Graph:

    @app.callback(
        Output(component_id={"type": ids.GAZE_SCATTER_PLOT, "index": roi}, component_property="figure"),
        Input(component_id=ids.FILTERS, component_property="data"),
        Input(component_id=ids.METRICS, component_property="data"),
        Input(component_id=ids.HIGHLIGHT_IDXS, component_property="data")
    )
    def update(all_filters, all_metrics, highlight_idxs) -> go.Figure:
        return update_scatter(patient=patient, roi=roi, highlight_idxs=highlight_idxs)



    fig = go.Figure()
    plot_active_scatter(fig=fig, patient=patient, roi=roi)
    
    graph = dcc.Graph(
        className="scatter-plot",
        id={"type": ids.GAZE_SCATTER_PLOT, "index": roi},
        figure=fig
    )

    return graph