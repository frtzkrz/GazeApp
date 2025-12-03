from config import *
from GazeOptimizer.patient_functions.helpers import get_angle_from_key, get_angles_from_keys
from GazeOptimizer.patient_functions.patient import Metric
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import matplotlib.cm as cm


# ============================================================
# CALLBACK HELPERS
# ============================================================

def get_new_click(last_click, this_click):
    for last, this in zip(last_click, this_click):
        if this is None: 
            continue
        elif this == last: 
            continue
        else: return this

def make_colorscale(plans, roi, metric, n_colors=256):
    """
    Create a Plotly colorscale based on the range of `values` using the Viridis colormap.
    Returns a list usable as `colorscale` in Plotly.
    """
    if metric is None:
        values = [plan.dvhs[roi].get_dvh_auc() for plan in plans]

    elif metric.metric_type in ['D', 'V']:
        values = [plan.dvhs[roi].get_metric_value(metric) for plan in plans]
    
    else: print('Metric Invalid')

    vmin, vmax = np.min(values), np.max(values)
    cmap = cm.get_cmap("viridis", n_colors)

    colorscale = []
    for i in range(n_colors):
        # normalized position (0–1) in the colorscale
        frac = i / (n_colors - 1)

        # get RGBA from matplotlib colormap
        r, g, b, _ = cmap(frac)

        # convert to rgb string
        color_str = f"rgb({int(r*255)}, {int(g*255)}, {int(b*255)})"

        colorscale.append([frac, color_str])
    return colorscale, values

def get_line_color(value, values, colorscale):
    """
    Return the exact color corresponding to `value`
    based on the colorscale created from `values`.
    Assumes `value` is one of the original values.
    """
    values = np.array(values, dtype=float)
    vmin, vmax = values.min(), values.max()

    # normalize value to 0–1 exactly the same way as Plotly
    frac = (value - vmin) / (vmax - vmin)

    # find the closest matching entry in the colorscale
    # because colorscale is defined on uniform 0–1 steps
    positions = np.array([p for p, _ in colorscale])
    idx = np.argmin(np.abs(positions - frac))

    return colorscale[idx][1]


def plot_dvh(subplot, roi, plan, value, metric, line_args={"width": 2}, opacity=1.):
    if plan.angle_key_2:
        w = np.round(plan.beam_weight, 1)
        metric_str = f"{w}*{plan.angle_key}° + {1-w}*{plan.angle_key_2}°<br>"
    
    else:
        metric_str = f"{plan.angle_key}°<br>"
    metric_str += "<br>"
    metric_str += "AUC: " if metric is None else f"{metric.metric_type}{metric.metric_value}: "
    metric_str += str(np.round(value, 1))
    hoverinfo = "skip" if opacity < 0.5 else "all"

    dvh = plan.dvhs[roi]
    subplot.add_trace(
        go.Scatter(
            x=dvh.dose,
            y=dvh.volume,
            mode="lines",
            line=line_args,
            opacity=opacity,
            hoverinfo=hoverinfo,
            hovertemplate=
                'D: %{x:.1f}<br>' +
                'V: %{y:.1f}<br>' +
                metric_str,
            
        ),
        row=1, col=1
    )

def plot_scatter(subplot, plans, colors, metric=None, colorscale=None, opacity=1., showscale=False):
    angle_keys = [plan.angle_key for plan in plans if not plan.angle_key_2]
    polars, thetas = get_angles_from_keys(angle_keys=angle_keys, azimuthal_as_radian=False)
    title = 'Area under DVH' if metric is None else metric.name
    subplot.add_trace(
        go.Scatterpolar(
            theta=thetas,
            r=polars,
            mode="markers",
            marker=dict(
                size=15,
                color=colors,
                colorscale=colorscale,
                colorbar=dict(title=title),
                showscale=showscale,
                opacity=opacity
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
        ),
        row=1, col=2
    )

def plot_metric(subplot, metric):
    if metric.metric_type == 'D':
        subplot.add_hline(
            y=metric.metric_value,
            line=dict(color='grey', width=2, dash='dash'),
            opacity=0.5,
            row=1, col=1
        ),
        
        
    elif metric.metric_type == 'V':
        subplot.add_vline(
            x=metric.metric_value,
            line=dict(color='grey', width=2, dash='dash'),
            opacity=0.5,
            row=1, col=1
        ),

    

def make_dvh_figure(roi, plans, highlight_plans, metric=None, all_plans=ALL_PLANS):
    fig = make_subplots(
        rows=1, cols=2,
        specs=[[{"type": "xy"}, {"type": "polar"}]],
        column_widths=[0.75, 0.25],
        subplot_titles=[ "DVH", "Gaze Angle"]
    )
    
    if len(plans) > 0:
        colorscale, values = make_colorscale(plans=plans, roi=roi, metric=metric)
    _, all_values = make_colorscale(plans=all_plans, roi=roi, metric=metric)

    old_plans = get_old_plans(plans=plans, all_plans=all_plans)

    #Plot old plans in grey
    for plan, value in zip(all_plans, all_values):

        #Plot old plans in grey
        if plan in old_plans:
            plot_dvh(subplot=fig, roi=roi, plan=plan, value=value, metric=metric, line_args={"color": "grey"}, opacity=0.1)


        #plot remaining plans according to metric
        elif plan not in highlight_plans:
            color = get_line_color(value, values=values, colorscale=colorscale)
            plot_dvh(subplot=fig, roi=roi, plan=plan, value=value, metric=metric, line_args={"color": color}, opacity=0.7)


    #plot highlighted plans
    if len(highlight_plans) > 0:
        _, highlight_values = make_colorscale(plans=highlight_plans, roi=roi, metric=metric)
        for plan, value in zip(highlight_plans, values):    
            dash = 'dot' if plan in old_plans else None
            plot_dvh(subplot=fig, roi=roi, plan=plan, value=value, metric=metric, line_args={"width": 3, "color": highlight_plans[plan], "dash": dash})
        
    if metric is not None:
        plot_metric(subplot=fig, metric=metric)

    

    #circle highlighted gaze angles
    highlight_scatter(subplot=fig, highlight_plans=highlight_plans)

    #Plot gaze angles
    plot_scatter(subplot=fig, plans=old_plans, colors=["grey"]*len(old_plans), opacity=0.3)
    if len(plans) > 0:
        plot_scatter(subplot=fig, plans=plans, metric=metric, colorscale=colorscale, colors=values, showscale=True)
    

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


def update_figures(plans, metrics, highlight_plans):    
    return [
        make_dvh_figure(roi=roi, plans=plans, metric=metrics[i], highlight_plans=highlight_plans)
        for i, roi in enumerate(ROI_NAMES)
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


def construct_metrics(metric_type_vals, metric_value_vals):
    metrics = []
    for roi, m_type, m_value in zip(ROI_NAMES, metric_type_vals, metric_value_vals):
        metrics.append(Metric(roi=roi, metric_type=m_type, metric_value=float(m_value)) if m_type in ["D", "V"] else None)
    return metrics

def no_message():
    n = len(ROI_NAMES)
    [""]*n, [{"display": "none"}]*n

def add_filter_from_metric(metrics, max_vals, filter_dict):
    for metric, max_val, roi in zip(metrics, max_vals, ROI_NAMES):
        if max_val:
            if metric.metric_type == 'D':
                filter_dict[roi] = {'dose': float(max_val), 'volume': metric.metric_value}
            else:
                filter_dict[roi] = {'dose': metric.metric_value, 'volume': float(max_val)}
    return filter_dict

