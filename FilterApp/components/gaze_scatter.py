from __future__ import annotations

from dash import Dash, dcc, html
import plotly.graph_objs as go
from . import ids
from utils.config import *
import plotly.express as px


from models.patient import Patient

def render(app: Dash, patient: Patient, roi: str) -> tuple[dcc.Graph, list[str]]:

    

    thetas = [plan.theta_1 for plan in patient.plans if not plan.two_beam]
    polars = [plan.polar_1 for plan in patient.plans if not plan.two_beam]
    values = [plan.dvhs[roi].metric_value for plan in patient.plans]

    numeric_values = [v for v in values if v is not None]
    vmin, vmax = min(numeric_values), max(numeric_values)
    colors = [
        str(px.colors.sample_colorscale(COLOR_SCALE, (v - vmin) / (vmax - vmin))[0]) if v is not None else 'grey'
        for v in values
    ]
    for plan, color in zip(patient.plans, colors):
        plan.dvhs[roi].color = color
    
    fig = go.Figure()

    fig.add_trace(trace=go.Scatterpolar(
            theta=thetas,
            r=polars,
            mode="markers",
            marker=dict(
                size=15,
                color=numeric_values,
                colorscale=COLOR_SCALE,
                colorbar=dict(title=patient.plans[0].dvhs[roi].metric_title, thickness=20, x=1.1),
                showscale=True,
            ),
            
        )
    )

    fig.update_layout(margin=dict(l=MARGIN_SIDE, r=MARGIN_SIDE, t=MARGIN_TOP, b=MARGIN_TOP))

    graph = dcc.Graph(
        className="scatter-plot",
        id={"type": ids.GAZE_SCATTER_PLOT, "index": roi},
        figure=fig
    )

    return graph, colors