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

    dcc.Store(id="clicked-points-store", data={}),

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
                    figure=make_dvh_figure(roi, plans=ALL_PLANS)
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
    Output("clicked-points-store", "data"),
    Input({"type": "roi-plot", "index": ALL}, "clickData"),
    Input({"type": "clear-button", "index": ALL}, "n_clicks"),
    Input({"type": "dose-metric-slider", "index": ALL}, "clickData"), #replace clickData 
    Input({"type": "volume-metric-slider", "index": ALL}, "clickData"), #replace clickData
    State("clicked-points-store", "data"),
)

def update(
    filter_clicks,
    clear_clicks,
    dose_slider,
    volume_slider,
    filter_dict,
):
    filter_dict = filter_dict or {}
    ctx = callback_context
    
    #avoid doing stuff when first loading page
    if not ctx.triggered:
        fig = update_figures(plans=ALL_PLANS)
        return fig, filter_dict
    
    #check if click on plots triggered callback
    if ctx.triggered_id['type'] == 'roi-plot': 
        filter_dict = add_filter(filter_dict=filter_dict, filter_clicks=filter_clicks)
    
    #check if click on "Clear Filter"
    if ctx.triggered_id['type'] == 'clear-button': 
        roi = ROI_NAMES[ctx.triggered_id['index']]
        filter_dict = delete_filter(filter_dict=filter_dict, roi=roi)
    new_plans = filter_plans(filter_dict=filter_dict, plans=ALL_PLANS)
    if len(new_plans) == 0:
        pass
    fig = update_figures(plans=new_plans)
    fig = add_filter_marker(fig=fig, filter_dict=filter_dict)


    #store_data[ROI_NAMES[i]] = {'dose': x, 'volume': y}


    #print(roi, which_plot)
    return fig, filter_dict
    #return fig, filter_dict
    #return fig, filter_dict#figure

# ============================================================
# RUN SERVER
# ============================================================

if __name__ == "__main__":
    app.run(debug=True)
