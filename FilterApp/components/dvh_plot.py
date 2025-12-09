from dash import Dash, dcc, Output, Input, ALL, State, Patch, callback_context
from models.patient import Patient
import plotly.graph_objs as go
from . import ids
from utils.config import *
import numpy as np

def render(app: Dash, patient: Patient, roi: str, colors: tuple[str]) -> dcc.Graph:

    traces: list[go.Scatter] = []

    for i, (plan, color) in enumerate(zip(patient.plans, colors)):
        patient.trace_uids[plan.uid] = i
        traces.append(
            go.Scatter(
                x=plan.dvhs[roi].dose,
                y=plan.dvhs[roi].volume,
                mode="lines",
                line={"color": color},
                showlegend=False,
                uid=plan.uid,
                hovertemplate=plan.hovertemplate+f"<br>{plan.dvhs[roi].metric_title}: {np.round(plan.dvhs[roi].metric_value)}"
            )
        )
    
    fig = go.Figure()
    [fig.add_trace(trace=trace) for trace in traces]

    patient.trace_uids["filter-point"] = len(patient.plans)
    #add invisible filter point
    fig.add_trace(
        trace=go.Scatter(
            x=[0],
            y=[0],
            mode="markers",
            marker={"size": 12, "color": "red"},
            showlegend=False,
            hoverinfo="none",
            visible=False,
            uid="filter-point",
        )
    )

    metric_type = ESPENSEN_METRICS[roi]["type"]
    metric_value = ESPENSEN_METRICS[roi]["value"]
    if metric_type == 'D':
        fig.add_hline(
            y=metric_value, 
            visible=True,
            line=dict(color="grey", width=2, dash="dash"),
            opacity=METRIC_OPACITY,
            name="hline"
        )

        fig.add_vline(
            x=0, 
            visible=False,
            line=dict(color="grey", width=2, dash="dash"),
            opacity=METRIC_OPACITY,
            name="vline"
        )
    elif metric_type == 'V':
        fig.add_hline(
            y=0, 
            visible=False,
            line=dict(color="grey", width=2, dash="dash"),
            opacity=METRIC_OPACITY,
            name="hline"
        )
        
        fig.add_vline(
            x=metric_value, 
            visible=True,
            line=dict(color="grey", width=2, dash="dash"),
            opacity=METRIC_OPACITY,
            name="vline"
        )
    
    else:
        fig.add_hline(
            y=0, 
            visible=False,
            line=dict(color="grey", width=2, dash="dash"),
            opacity=METRIC_OPACITY,
            name="hline"
        )
        fig.add_vline(
            x=0, 
            visible=False,
            line=dict(color="grey", width=2, dash="dash"),
            opacity=METRIC_OPACITY,
            name="vline"
        )

    fig.update_layout(
        title=roi, 
        margin=dict(l=30, r=0, t=MARGIN_TOP, b=MARGIN_TOP),
    )



    graph = dcc.Graph(
        className="dvh-plot",
        id={"type": ids.DVH_PLOT, "index": roi},
        figure=fig
    )
    
    return graph