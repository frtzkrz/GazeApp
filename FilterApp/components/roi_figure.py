from __future__ import annotations

from dash import Dash, dcc, html, Input, Output, State, callback_context, ALL, Patch
import plotly.graph_objs as go
from . import ids
from utils.config import *
import plotly.express as px

from components import gaze_scatter, dvh_plot

from models.patient import Patient
from models.metric import Metric

from components.roi_figure_helpers import update_filters, update_metrics

def render(app: Dash, patient: Patient, roi: str) -> html.Div:

    #Update metrics
    @app.callback(
        Output(component_id={"type": ids.METRIC, "index": roi}, component_property="data"),
        Output(component_id={"type": ids.METRIC_VALUE_FIELD, "index": roi}, component_property="value"),
        Input(component_id={"type": ids.APPLY_METRIC_BUTTON, "index": roi}, component_property="n_clicks"),
        State(component_id={"type": ids.METRIC, "index": roi}, component_property="data"),
        State(component_id={"type": ids.METRIC_VALUE_FIELD, "index": roi}, component_property="value"),
        State(component_id={"type": ids.METRIC_TYPE_DROPDOWN, "index": roi}, component_property="value"),
    )

    def metrics_callback(_, roi_metric: dict[str, dict[str, int | str | None]], metric_value: float | int | None, metric_type: str | None) -> tuple[dict[str, dict[str, int | str | None]], int | None]:
        return update_metrics(
                roi=roi,
                roi_metric=roi_metric,
                metric_value=metric_value,
                metric_type=metric_type
        )



    #Update filters
    @app.callback(
        Output(component_id={"type": ids.FILTER, "index": roi}, component_property="data"),
        Output(component_id={"type": ids.METRIC_MAX_FIELD, "index": roi}, component_property="value"),
        Input(component_id={"type": ids.CLEAR_FILTER_BUTTON, "index": roi}, component_property="n_clicks"),
        Input(component_id={"type": ids.APPLY_FILTER_BUTTON, "index": roi}, component_property="n_clicks"),
        Input(component_id={"type": ids.DVH_PLOT, "index": roi}, component_property="clickData"),
        State(component_id={"type": ids.FILTER, "index": roi}, component_property="data"),
        State(component_id={"type": ids.METRIC_TYPE_DROPDOWN, "index": roi}, component_property="value"),
        State(component_id={"type": ids.METRIC_VALUE_FIELD, "index": roi}, component_property="value"),
        State(component_id={"type": ids.METRIC_MAX_FIELD, "index": roi}, component_property="value"),   
    )

    def filters_callback(_, __, dvh_click, roi_filter, metric_type, metric_value, metric_max) -> tuple[dict[str, list[int | None]], int | None]:
        return update_filters(
            roi=roi,
            ctx=callback_context,
            dvh_click=dvh_click,
            roi_filter=roi_filter,
            metric_type=metric_type, 
            metric_value=metric_value,
            metric_max=metric_max
        )

    scatter_graph = gaze_scatter.render(app=app, patient=patient, roi=roi)
    dvh_graph = dvh_plot.render(app=app, patient=patient, roi=roi) # type: ignore

    return html.Div(
        className="roi-figure",
        id={"type": ids.ROI_FIGURE, "index": roi},
        children=[
            dvh_graph,
            scatter_graph,
        ]
    )