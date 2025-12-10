from utils.config import *
import plotly.graph_objs as go
from models.patient import Patient


def get_highlight_angles(patient: Patient, highlight_idx: dict[str, str]) -> tuple[list, list]:
    highlights = [int(h) for h in highlight_idx.keys()]
    plans = [plan for plan in patient.plans if patient.trace_uids[plan.uid] in highlights]
    thetas = [plan.theta_1 for plan in plans]
    polars = [plan.polar_1 for plan in plans]
    return polars, thetas


def get_angles(patient: Patient, active=True) -> tuple[list[float], list[float]]:

    if active:
        thetas = [plan.theta_1 for plan in patient.plans if not plan.two_beam and plan in patient.active_plans]
        polars = [plan.polar_1 for plan in patient.plans if not plan.two_beam and plan in patient.active_plans]

    else: 
        thetas = [plan.theta_1 for plan in patient.plans if not plan.two_beam and plan not in patient.active_plans]
        polars = [plan.polar_1 for plan in patient.plans if not plan.two_beam and plan not in patient.active_plans]
    
    return polars, thetas

def get_value_infos(patient: Patient, roi: str) -> tuple[list[float], float, float]:
    numeric_values = [plan.dvhs[roi].metric_value for plan in patient.plans]
    scatter_values = [v for v, plan in zip(numeric_values, patient.plans) if not plan.two_beam and plan in patient.active_plans]
    vmin, vmax = min(numeric_values), max(numeric_values)
    
    return scatter_values, vmin, vmax

def plot_active_scatter(fig: go.Figure, patient: Patient, roi: str):
    polars, thetas = get_angles(patient=patient, active=True)
    scatter_values, vmin, vmax = get_value_infos(patient=patient, roi=roi)
    fig.add_trace(
        trace=go.Scatterpolar(
            theta=thetas,
            r=polars,
            mode="markers",
            showlegend=False,
            marker=dict(
                size=15,
                cmin=vmin,
                cmax=vmax,
                color=scatter_values,
                colorscale=COLOR_SCALE,
                colorbar=dict(title=patient.plans[0].dvhs[roi].metric_title, thickness=20, x=1.1),
                showscale=True,
                opacity=ACTIVE_OPACITY,
            ),     
        )
    )

def plot_highlight_scatter(fig: go.Figure, patient: Patient, roi: str, highlight_idxs: dict[str, str]):
    polars, thetas = get_highlight_angles(patient=patient, highlight_idx=highlight_idxs)
    colors = [highlight_idxs[idx] for idx in highlight_idxs]
    fig.add_trace(
        trace=go.Scatterpolar(
            theta=thetas,
            r=polars,
            mode="markers",
            showlegend=False,
            marker=dict(
                size=18,
                color=colors,
                symbol="circle-open",
                line=dict(width=3),
                opacity=HIGHLIGHT_OPACITY,
                showscale=False,
            ),     
        )
    )




def plot_passive_scatter(fig: go.Figure, patient: Patient, roi: str) -> None:
    polars, thetas = get_angles(patient=patient, active=False)
    fig.add_trace(
        trace=go.Scatterpolar(
            theta=thetas,
            r=polars,
            mode="markers",
            showlegend=False,
            marker=dict(
                size=15,
                color="grey",
                opacity=PASSIVE_OPACITY,
                showscale=False,
            ),     
        )
    )



def update_scatter(patient, roi, highlight_idxs) -> go.Figure:

    fig = go.Figure()

    plot_active_scatter(fig=fig, patient=patient, roi=roi)
    plot_passive_scatter(fig=fig, patient=patient, roi=roi)
    plot_highlight_scatter(fig=fig, patient=patient, roi=roi, highlight_idxs=highlight_idxs)

    fig.update_layout(margin=dict(l=MARGIN_SIDE, r=MARGIN_SIDE, t=MARGIN_TOP, b=MARGIN_TOP))
    

    return fig

