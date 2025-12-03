import numpy as np
import dash
from dash import html, dcc, callback_context
from dash.dependencies import Input, Output, State, MATCH, ALL
import plotly.graph_objs as go
import matplotlib as mpl

from helpers import *
from config import *


# ============================================================
# DASH APP
# ============================================================

app = dash.Dash(__name__)

m_types = [ESPENSEN_METRICS[roi][0] for roi in ROI_NAMES]
m_vals = [ESPENSEN_METRICS[roi][1] for roi in ROI_NAMES]
ESPENSEN_METRICS = construct_metrics(m_types, m_vals)

app.layout = html.Div([

    dcc.Store(id="filters", data={}),
    dcc.Store(id="last-click", data=[None for _ in ROI_NAMES]),
    dcc.Store(id="highlight-plans", data={}),

    html.Div(
        id="plots-container",
        style={
            "display": "grid",
            "gridTemplateColumns": "1fr auto",
            "gap": "20px",
            "alignItems": "start"
        },
        children=[
            html.Div([
                dcc.Graph(
                    id={"type": "roi-plot", "index": i},
                    figure=make_dvh_figure(roi, plans=ALL_PLANS, metric=ESPENSEN_METRICS[i], highlight_plans=[])
                ),
                html.Button(
                    "Clear Filter",
                    id={"type": "clear-button", "index": i},
                    n_clicks=0,
                    style={"marginLeft": "10px"}
                ),
                dcc.Input(
                    id={"type": "metric-type", "index": i},
                    type='text',
                    placeholder='D/V',
                    style={
                        "marginLeft": "100px",
                        "width": "50px"
                    },
                    value=ESPENSEN_METRICS[i].metric_type if ESPENSEN_METRICS[i] is not None else None
                ),
                dcc.Input(
                    id={"type": "metric-value", "index": i},
                    type='text',
                    placeholder='value',
                    style={"width": "50px"},
                    value=ESPENSEN_METRICS[i].metric_value if ESPENSEN_METRICS[i] is not None else None
                ),
                dcc.Input(
                    id={"type": "metric-max", "index": i},
                    type='text',
                    placeholder='max',
                    style={"width": "50px"}
                ),
                html.Button(
                    "Apply",
                    id={"type": "apply-button", "index": i},
                    n_clicks=0,
                    style={"marginLeft": "10px"}
                ),
                html.Div(
                    id={'type': 'message-box', 'index': i},
                    style={
                        'color': 'red',
                        'margin-top': '5px',
                        'display': 'none'  # hidden by default
                    }
                ),
            ])
            for i, roi in enumerate(ROI_NAMES)
        ]
    )
])





# ============================================================
# CALLBACK: CLICK TO SET FILTER
# ============================================================

# Update figures and filter store
@app.callback(
    Output({"type": "roi-plot", "index": ALL}, "figure"),
    Output("filters", "data"),
    Output("last-click", "data"),
    Output("highlight-plans", "data"),
    Output({'type': 'metric-max', 'index': ALL}, 'value'),
    Input({"type": "roi-plot", "index": ALL}, "clickData"),
    Input({"type": "clear-button", "index": ALL}, "n_clicks"),
    Input({"type": "apply-button", "index": ALL}, "n_clicks"),
    State("filters", "data"),
    State("last-click", "data"),
    State("highlight-plans", "data"),
    State({'type': 'metric-type', 'index': ALL}, 'value'),
    State({'type': 'metric-value', 'index': ALL}, 'value'),
    State({'type': 'metric-max', 'index': ALL}, 'value'),
)

def update(
    filter_clicks,
    clear_clicks,
    apply_clicks,
    filter_dict,
    last_click,
    highlight_plan_keys,
    metric_type_vals,
    metric_value_vals,
    metric_max_vals,
):  
    metrics = construct_metrics(metric_type_vals, metric_value_vals)
    ctx = callback_context
    highlight_point = None

    #avoid doing stuff when first loading page
    if not ctx.triggered:
        fig = update_figures(plans=ALL_PLANS, metrics=metrics, highlight_plans=[])
        return fig, filter_dict, last_click, highlight_plan_keys, metric_max_vals
    


    #extract Roi Name and Point Data
    roi = ROI_NAMES[ctx.triggered_id['index']]
    
    #create filter store
    filter_dict = filter_dict or {}
    

    
    #check if click on plots triggered callback
    if ctx.triggered_id['type'] == 'roi-plot':
        point = get_new_click(last_click=last_click, this_click=filter_clicks)["points"][0]
        if "x" in point: filter_dict = add_filter(filter_dict=filter_dict, point=point, roi=roi)
        elif "r" in point:
            highlight_point = point
    
    #check if metric max was specified. if so, add/adjust filter
    if any(metric_max_vals):
        filter_dict = add_filter_from_metric(
            metrics=metrics, 
            max_vals=metric_max_vals, 
            filter_dict=filter_dict
        )
        
    #check if click on "Clear Filter"
    if ctx.triggered_id['type'] == 'clear-button':
        filter_dict = delete_filter(filter_dict=filter_dict, roi=roi)
        roi_idx = ROI_NAMES.index(roi)
        metric_max_vals[roi_idx] = None            
    
    #update plans
    new_plans = filter_plans(filter_dict=filter_dict, plans=ALL_PLANS)

    if highlight_point is not None:
        add_highlight(highlight_plan_keys=highlight_plan_keys, point=highlight_point)

    highlight_plans = {plan: highlight_plan_keys[plan.angle_key] for plan in ALL_PLANS if plan.angle_key in highlight_plan_keys and not plan.angle_key_2}
    #display message if no plans left
    if len(new_plans) == 0:
        print("No Plans left")


    #update figures and add markers from filter_dict
    fig = update_figures(plans=new_plans, metrics=metrics, highlight_plans=highlight_plans)
    fig = add_filter_marker(fig=fig, filter_dict=filter_dict)
    #print(highlight_plan_keys)
    return fig, filter_dict, filter_clicks, highlight_plan_keys, metric_max_vals


# ============================================================
# RUN SERVER
# ============================================================

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
