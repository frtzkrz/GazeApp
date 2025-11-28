from config import *
from GazeOptimizer.patient_functions.helpers import get_angle_from_key, get_angles_from_keys
import plotly.graph_objs as go
from plotly.subplots import make_subplots


# ============================================================
# CALLBACK HELPERS
# ============================================================
def make_dvh_figure(roi, plans, all_plans=ALL_PLANS):
    fig = make_subplots(
        rows=1, cols=2,
        specs=[[{"type": "xy"}, {"type": "polar"}]],
        column_widths=[0.75, 0.25],
        subplot_titles=[ "DVH", "Gaze Angle"]
    )
    angle_keys = [plan.angle_key for plan in plans]
    polars, thetas = get_angles_from_keys(angle_keys=angle_keys, azimuthal_as_radian=False)
    aucs = [plan.dvhs[roi].get_dvh_auc() for plan in plans]
    norm = mpl.colors.Normalize(vmin=min(aucs), vmax=max(aucs))
    normalized_aucs = norm(aucs)
    colors = [f"rgb{tuple(int(255*c) for c in CMAP(auc)[:3])}" for auc in normalized_aucs]

    old_plans = get_old_plans(plans=plans, all_plans=all_plans)

    for plan in old_plans:
        dvh = plan.dvhs[roi]
        fig.add_trace(
            go.Scatter(
                x=dvh.dose,
                y=dvh.volume,
                mode="lines",
                line=dict(width=2, color='grey'),
                opacity=0.3,
                hovertemplate=
                    'D: %{x:.1f}<br>' +
                    'V: %{y:.1f}<br>' +
                    f'{plan.angle_key}'
            ),
            row=1, col=1
        )

    for plan, color in zip(plans, colors):
        dvh = plan.dvhs[roi]
        fig.add_trace(
            go.Scatter(
                x=dvh.dose,
                y=dvh.volume,
                mode="lines",
                line=dict(width=2, color=color),
                opacity=1.,
                hovertemplate=
                    'D: %{x:.1f}<br>' +
                    'V: %{y:.1f}<br>' +
                    f'{plan.angle_key}'
            ),
            row=1, col=1
        )

    fig.add_trace(
        go.Scatterpolar(
            theta=thetas,
            r=polars,
            mode="markers",
            marker=dict(
                size=15,
                color=aucs,
                colorscale='Viridis',
                colorbar=dict(title='Area under DVH'),
                showscale=True
            )
            
        ),
        row=1, col=2
    )

    fig.update_layout(
        title=roi,
        showlegend=False,
        margin=dict(l=10, r=10, t=25, b=10),
        height=FIGSIZE_Y,
        width=FIGSIZE_X,
    )
    fig.update_xaxes(title="Dose [Gy]", row=1, col=1)
    fig.update_yaxes(title="Volume [%]", row=1, col=1)

    return fig

def get_old_plans(plans, all_plans=ALL_PLANS):
    return [plan for plan in all_plans if plan not in plans]


def add_filter(filter_dict, filter_clicks):
    for clickData, roi in zip(filter_clicks, ROI_NAMES): #iterate through all ROIs
        if clickData is None:
            continue
        point = clickData["points"][0]
        

        if "x" in point:
            x, y = point["x"], point["y"]
            dvh_point = (x, y)
            filter_dict = update_after_filter_click(filter_dict=filter_dict, roi=roi, dvh_point=dvh_point)
    return filter_dict


def delete_filter(filter_dict, roi):
    if roi in filter_dict:
        del filter_dict[roi]
    return filter_dict

def update_after_filter_click(filter_dict, roi, dvh_point):
    x, y = dvh_point
    filter_dict[roi] = {'dose': x, 'volume': y}
    
    return filter_dict


def update_figures(plans):    
    return [
        make_dvh_figure(roi=roi, plans=plans)
        for roi in ROI_NAMES
    ]

def filter_plans(filter_dict, plans=ALL_PLANS):
    for roi in filter_dict:
        plans = [plan for plan in plans if plan.dvhs[roi].get_dose_at_volume(filter_dict[roi]['volume']) < filter_dict[roi]['dose']+EPS]
    return plans

def clear_filters(filter_dict, roi):
    if roi in filter_dict:
        del filter_dict[roi]
    return filter_dict




def add_filter_marker(fig, filter_dict):

    for f, roi in zip(fig, ROI_NAMES):
        if roi in filter_dict:
            point = filter_dict[roi]
            f.add_trace(
                go.Scatter(
                    x=[point['dose']],
                    y=[point['volume']],
                    mode="markers",
                    marker=dict(color="red", size=15),
                    name="Selected Point"
                ),
            )
    return fig