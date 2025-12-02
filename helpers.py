from config import *
from GazeOptimizer.patient_functions.helpers import get_angle_from_key, get_angles_from_keys
from GazeOptimizer.patient_functions.patient import Metric
import plotly.graph_objs as go
from plotly.subplots import make_subplots


# ============================================================
# CALLBACK HELPERS
# ============================================================

def get_new_click(last_click, this_click):
    for last, this in zip(last_click, this_click):
        #print(f"this: {this}, last: {last}")
        if this is None: 
            continue
        elif this == last: 
            continue
        else: return this



def get_colors(plans, roi, metric):
    if metric is None:
        aucs = [plan.dvhs[roi].get_dvh_auc() for plan in plans]
        norm = mpl.colors.Normalize(vmin=min(aucs), vmax=max(aucs))
        normalized_aucs = norm(aucs)
        colors = [f"rgb{tuple(int(255*c) for c in CMAP(auc)[:3])}" for auc in normalized_aucs]


    else:
        metrics = [plan.dvhs[roi].get_metric_value(metric) for plan in plans]
        norm = mpl.colors.Normalize(vmin=min(metrics), vmax=max(metrics))
        normalized_metrics = norm(aucs)
        colors = [f"rgb{tuple(int(255*c) for c in CMAP(metric)[:3])}" for metric in normalized_metrics]

    return colors

def plot_dvh(subplot, roi, plan, line_args={"width": 2}, opacity=1.):
    dvh = plan.dvhs[roi]
    subplot.add_trace(
        go.Scatter(
            x=dvh.dose,
            y=dvh.volume,
            mode="lines",
            line=line_args,
            opacity=opacity,
            hovertemplate=
                'D: %{x:.1f}<br>' +
                'V: %{y:.1f}<br>' +
                f'{plan.angle_key}'
        ),
        row=1, col=1
    )

def plot_scatter(subplot, plans, colors, opacity=1.):
    angle_keys = [plan.angle_key for plan in plans]
    polars, thetas = get_angles_from_keys(angle_keys=angle_keys, azimuthal_as_radian=False)
    

    subplot.add_trace(
        go.Scatterpolar(
            theta=thetas,
            r=polars,
            mode="markers",
            marker=dict(
                size=15,
                color=colors,
                colorscale='Viridis',
                colorbar=dict(title='Area under DVH'),
                opacity=opacity,
                showscale=True
            )
            
        ),
        row=1, col=2
    )

def highlight_scatter(subplot, highlight_plans):
    angle_keys = [plan.angle_key for plan in highlight_plans]
    polars, azimuthals = get_angles_from_keys(angle_keys=angle_keys, azimuthal_as_radian=False)
    colors = [highlight_plans[plan] for plan in highlight_plans]
    subplot.add_trace(
        go.Scatterpolar(
            r=polars,
            theta=azimuthals,
            mode='markers',
            marker=dict(
                size=18,                 # bigger circle
                symbol="circle-open",    # open circle outline!
                line=dict(width=3),
                color=colors
            ),
        )
    )

def make_dvh_figure(roi, plans, highlight_plans, metric=None, all_plans=ALL_PLANS):
    fig = make_subplots(
        rows=1, cols=2,
        specs=[[{"type": "xy"}, {"type": "polar"}]],
        column_widths=[0.75, 0.25],
        subplot_titles=[ "DVH", "Gaze Angle"]
    )
    colors = get_colors(plans=plans, roi=roi, metric=metric)

    old_plans = get_old_plans(plans=plans, all_plans=all_plans)

    #Plot old plans in grey
    for plan in old_plans:
        plot_dvh(subplot=fig, roi=roi, plan=plan, line_args={"color": "grey"}, opacity=0.3)

    #Plot remaining plans in color
    for plan, color in zip(plans, colors):
        plot_dvh(subplot=fig, roi=roi, plan=plan, line_args={"color": color}, opacity=0.5)

    #Plot highlighted plans in contrasting colors
    for plan in highlight_plans:
        dash = 'dot' if plan in old_plans else None
        plot_dvh(subplot=fig, roi=roi, plan=plan, line_args={"width": 3, "color": highlight_plans[plan], "dash": dash})

    #Plot gaze angles
    plot_scatter(subplot=fig, plans=plans, colors=colors)
    plot_scatter(subplot=fig, plans=old_plans, colors=["grey"]*len(old_plans), opacity=0.3)

    #circle highlighted gaze angles
    highlight_scatter(subplot=fig, highlight_plans=highlight_plans)

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


def add_filter(filter_dict, point, roi):
    x, y = point["x"], point["y"]
    dvh_point = (x, y)
    filter_dict = update_after_filter_click(filter_dict=filter_dict, roi=roi, dvh_point=dvh_point)
    return filter_dict


def delete_filter(filter_dict, roi):
    new_filter = filter_dict.copy()
    if roi in new_filter:
        del new_filter[roi]
    return new_filter

def update_after_filter_click(filter_dict, roi, dvh_point):
    x, y = dvh_point
    filter_dict[roi] = {'dose': x, 'volume': y}
    
    return filter_dict


def update_figures(plans, highlight_plans):    
    return [
        make_dvh_figure(roi=roi, plans=plans, highlight_plans=highlight_plans)
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

def add_highlight(highlight_plan_keys, point):
    
    polar, theta = point['r'], point['theta']
    plan = find_plan_with_angles(polar, theta)
    plan_key = plan.angle_key
    if plan_key in highlight_plan_keys:
        del highlight_plan_keys[plan_key]
    else: highlight_plan_keys[plan_key] = next(HIGHLIGHT_COLORS)

def find_plan_with_angles(polar, theta):
    for plan in ALL_PLANS:
        plan_polar, plan_theta = get_angle_from_key(plan.angle_key, azimuthal_as_radian=False)
        if (plan_polar, plan_theta) == (polar, theta):
            return plan
     