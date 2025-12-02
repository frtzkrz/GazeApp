import numpy as np
import dash
from dash import html, dcc, callback_context
from dash.dependencies import Input, Output, State, MATCH, ALL
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import matplotlib as mpl

from helpers import *
from config import *


# ============================================================
# DASH APP
# ============================================================

app = dash.Dash(__name__)

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
                    figure=make_dvh_figure(roi, plans=ALL_PLANS, highlight_plans=[])
                ),
                html.Button(
                    "Clear Filter",
                    id={"type": "clear-button", "index": i},
                    n_clicks=0,
                    style={"marginLeft": "10px"}
                )
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
    Input({"type": "roi-plot", "index": ALL}, "clickData"),
    Input({"type": "clear-button", "index": ALL}, "n_clicks"),
    Input({"type": "dose-metric-slider", "index": ALL}, "clickData"), #replace clickData 
    Input({"type": "volume-metric-slider", "index": ALL}, "clickData"), #replace clickData
    State("filters", "data"),
    State("last-click", "data"),
    State("highlight-plans", "data"),
)

def update(
    filter_clicks,
    clear_clicks,
    dose_slider,
    volume_slider,
    filter_dict,
    last_click,
    highlight_plan_keys,
):  
    ctx = callback_context
    highlight_point = None

    #avoid doing stuff when first loading page
    if not ctx.triggered:
        fig = update_figures(plans=ALL_PLANS, highlight_plans=[])
        return fig, filter_dict, last_click, highlight_plan_keys
    
    #extract Roi Name and Point Data
    roi = ROI_NAMES[ctx.triggered_id['index']]
    
    #create filter store
    filter_dict = filter_dict or {}
    
    #check if click on "Clear Filter"
    if ctx.triggered_id['type'] == 'clear-button':
        filter_dict = delete_filter(filter_dict=filter_dict, roi=roi)
    
    #check if click on plots triggered callback
    if ctx.triggered_id['type'] == 'roi-plot':
        point = get_new_click(last_click=last_click, this_click=filter_clicks)["points"][0]
        if "x" in point: filter_dict = add_filter(filter_dict=filter_dict, point=point, roi=roi)
        elif "r" in point:
            highlight_point = point
            
    
    #update plans
    new_plans = filter_plans(filter_dict=filter_dict, plans=ALL_PLANS)

    if highlight_point is not None:
        add_highlight(highlight_plan_keys=highlight_plan_keys, point=highlight_point)

    highlight_plans = {plan: highlight_plan_keys[plan.angle_key] for plan in ALL_PLANS if plan.angle_key in highlight_plan_keys}
    #display message if no plans left
    if len(new_plans) == 0:
        pass

    #update figures and add markers from filter_dict
    fig = update_figures(plans=new_plans, highlight_plans=highlight_plans)
    fig = add_filter_marker(fig=fig, filter_dict=filter_dict)
    #print(highlight_plan_keys)
    return fig, filter_dict, filter_clicks, highlight_plan_keys


# ============================================================
# RUN SERVER
# ============================================================

if __name__ == "__main__":
    app.run(debug=True)
