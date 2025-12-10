from dash import Dash, html, Input, Output, ALL, MATCH, dcc, callback_context, State
import plotly.graph_objs as go
from models.patient import Patient
from models.plan import Plan
from . import roi_figure
from utils.config import *
from . import ids
from components.figures_helpers import update_active_plans, update_dvh_metrics, update_highlights

def create_figure(app: Dash, patient: Patient) -> html.Div:
    """
    Create a list of ROI figures (dcc.Graph) for all ROIs.
    Each Graph has a pattern-matching id for callbacks.
    """


    res = html.Div(
        children=[
            dcc.Store(id=ids.FILTERS, data={}),
            dcc.Store(id=ids.METRICS, data=ESPENSEN_METRICS),
            dcc.Store(id=ids.HIGHLIGHT_IDXS, data={}),
            html.Div(
                className="figures",
                children=[
                    html.Div(
                        className="roi-container",
                        children = [
                            roi_figure.render(app=app, patient=patient, roi=roi),
                            html.Div(
                                className="roi-controls",
                                children=[
                                    html.Button(className="clear-filter-button", children="Clear Filter", id={"type": ids.CLEAR_FILTER_BUTTON, "index": roi}, n_clicks=0),
                                    dcc.Dropdown(
                                        className="metric-type-dropdown",
                                        id={"type": ids.METRIC_TYPE_DROPDOWN, "index": roi},
                                        placeholder="V/D",
                                        options=[{"label": mt, "value": mt} for mt in METRIC_TYPES],
                                        value=ESPENSEN_METRICS[roi]["type"]
                                    ),
                                    dcc.Input(className="metric-value-field", id={"type": ids.METRIC_VALUE_FIELD, "index": roi}, type="number", placeholder="Value (Gy/%)", value=ESPENSEN_METRICS[roi]["value"]),
                                    html.Button(className="apply-button", children="Apply Metric", id={"type": ids.APPLY_METRIC_BUTTON, "index": roi}, n_clicks=0),
                                    dcc.Input(className="metric-value-field", id={"type": ids.METRIC_MAX_FIELD, "index": roi}, type="number", placeholder="Max (%/Gy)"),
                                    html.Button(className="apply-button", children="Apply Filter", id={"type": ids.APPLY_FILTER_BUTTON, "index": roi}, n_clicks=0),

                                    
                                ]
                            ),
                            dcc.Store(id={"type": ids.FILTER, "index": roi}, data={roi: [None, None]}),
                            dcc.Store(id={"type": ids.METRIC, "index": roi}, data={roi: {"type": None, "value": None}}),
                        ]
                    )
                for roi in ROI_NAMES  
                ]
            )
        ]
    )    

    return res

def render(app: Dash, patient: Patient) -> html.Div:
    """
    Returns a Div containing all ROI figures and registers the callback.
    The callback updates all figures when any is clicked.
    """    

    # adjust filters when any filter changes
    @app.callback(
        Output(component_id=ids.FILTERS, component_property="data"),
        Input(component_id={"type": ids.FILTER, "index": ALL}, component_property="data"),
    )
    def update_filters(roi_filters) -> dict[str, list[int]]:
        all_filters = {roi: filt for f_dict in roi_filters for roi, filt in f_dict.items()}
        update_active_plans(patient=patient, all_filters=all_filters)
        return all_filters 
    

    #adjust metrics when any metric changes
    @app.callback(
        Output(component_id=ids.METRICS, component_property="data"),
        Input(component_id={"type": ids.METRIC, "index": ALL}, component_property="data"),
        State(component_id=ids.METRICS, component_property="data"),
    )
    def update_metrics(roi_metrics, all_metrics) -> dict[str, dict[str, int | str | None]]:
        all_metrics = {roi: metric for m_dict in roi_metrics for roi, metric in m_dict.items()}
        update_dvh_metrics(patient=patient, all_metrics=all_metrics)
        return all_metrics
    

    #Handle clicks on scatterplot to highlight plans
    @app.callback(
        Output(component_id=ids.HIGHLIGHT_IDXS, component_property="data"),
        Output(component_id={"type": ids.GAZE_SCATTER_PLOT, "index": ALL}, component_property="clickData"),
        Input(component_id={"type": ids.GAZE_SCATTER_PLOT, "index": ALL}, component_property="clickData"),
        State(component_id=ids.HIGHLIGHT_IDXS, component_property="data"),
        prevent_initial_callback=True,
    )
    def register_highlight(clicks, highlight_idxs) -> tuple[dict[str, str], list]:
        return update_highlights(patient=patient, clicks=clicks, highlight_idxs=highlight_idxs), [None for _ in ROI_NAMES]
    
    
    update_dvh_metrics(patient=patient, all_metrics=STARTING_METRICS)
    return create_figure(app=app, patient=patient)