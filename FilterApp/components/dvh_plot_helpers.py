from utils.config import *

import plotly.graph_objects as go
from models.patient import Patient
from dash import dcc

from . import ids

def create_traces(patient, roi) -> list[go.Scatter]:
    traces: list[go.Scatter] = []
    for i, plan in enumerate(patient.plans):
        patient.trace_uids[plan.uid] = i
        traces.append(
            go.Scatter(
                x=plan.dvhs[roi].dose,
                y=plan.dvhs[roi].volume,
                mode="lines",
                line={"color": plan.dvhs[roi].color},
                opacity=ACTIVE_OPACITY,
                showlegend=False,
                uid=plan.uid,
                hovertemplate=plan.hovertemplate+"<br>"+plan.dvhs[roi].hover_info
            )
        )
    return traces


def add_filter_point(fig: go.Figure) -> None:
    #add invisible filter point
    fig.add_trace(
        trace=go.Scatter(
            x=[0],
            y=[0],
            mode="markers",
            marker={"size": 12, "color": "red"},
            showlegend=False,
            visible=False,
            uid="filter-point",
        )
    )

def create_figure(traces: list[go.Scatter]) -> go.Figure:
    fig = go.Figure()
    [fig.add_trace(trace=trace) for trace in traces]
    return fig

def add_metric_lines(fig, roi):
    metric_type = STARTING_METRICS[roi]["type"]
    metric_value = STARTING_METRICS[roi]["value"]

    if metric_type == 'D':
        x = 0
        y = metric_value
        visible_h = True
        visible_v = False

    elif metric_type == 'V':
        x = metric_value
        y = 0
        visible_h = False
        visible_v = True       

    else:
        x, y = 0, 0
        visible_h, visible_v = False, False

    fig.add_hline(
        y=y, 
        visible=visible_h,
        line=dict(color="grey", width=2, dash="dash"),
        opacity=METRIC_OPACITY,
        name="hline"
    )
    fig.add_vline(
        x=x, 
        visible=visible_v,
        line=dict(color="grey", width=2, dash="dash"),
        opacity=METRIC_OPACITY,
        name="vline"
    )


def create_dvh_plot(patient, roi) -> dcc.Graph:
    traces = create_traces(patient=patient, roi=roi)
    fig = create_figure(traces=traces)

    patient.trace_uids["filter-point"] = len(patient.plans)
    add_filter_point(fig=fig)
    add_metric_lines(fig=fig, roi=roi)
    fig.update_layout(
        title=roi, 
        margin=dict(l=30, r=0, t=MARGIN_TOP, b=MARGIN_TOP),
    )
    fig.update_xaxes(title="Dose [Gy]")
    fig.update_yaxes(title="Volume [%]")    
    
    graph = dcc.Graph(
        className="dvh-plot",
        id={"type": ids.DVH_PLOT, "index": roi},
        figure=fig
    )

    return graph

from dataclasses import dataclass
from . import ids
from typing import Any
from dash import Patch
from models.patient import Patient
from utils.config import *
import numpy as np

def update_metrics(roi, roi_metric, metric_value, metric_type) -> tuple[dict[str, dict[str, int | str | None]], int | None]:
    if metric_value is not None:
        metric_value = int(metric_value)

        if metric_type is not None:
            roi_metric[roi] = {"type": metric_type, "value": int(metric_value)}
    
    else:
        roi_metric[roi] = {"type": None, "value": None}

    return roi_metric, metric_value

def update_filters(roi, ctx, dvh_click, roi_filter, metric_type, metric_value, metric_max) -> tuple[dict[str, list[int | None]], int | None]:
    trigger = ctx.triggered_id["type"] if ctx.triggered_id else None
    if trigger == ids.CLEAR_FILTER_BUTTON:
        roi_filter[roi] = [None, None]
        metric_max = None

    elif trigger == ids.APPLY_FILTER_BUTTON:
        if metric_max is not None:
            if metric_type is not None and metric_value is not None:
                if  metric_type == "V":
                    roi_filter[roi] = [int(metric_value), int(metric_max)]
                elif metric_type == "D":
                    roi_filter[roi] = [int(metric_max), int(metric_value)]

    elif trigger == ids.DVH_PLOT:
        dose, vol = dvh_click["points"][0]["x"], dvh_click["points"][0]["y"] # if dvh_click else roi_filter[roi]
        roi_filter[roi] = [int(dose), int(vol)]
    return roi_filter, metric_max

def update_filter_point(patch: Patch, patient: Patient, roi: str, all_filters: dict[str, list[int]]) -> None:
    idx = patient.trace_uids["filter-point"]
    if all_filters[roi] == [None, None]:
        patch["data"][idx]["visible"] = False
        #patch["data"][idx]["hoverinfo"] = False

    else:
        dose, volume = all_filters[roi]
        patch["data"][idx]["visible"] = True
        patch["data"][idx]["hoverinfo"] = True
        patch["data"][idx]["hovertemplate"] = f"D: {dose}, V: {volume}",
        patch["data"][idx]["x"] = [dose]
        patch["data"][idx]["y"] = [volume]

def update_active_plans(patient: Patient, all_filters: dict[str, list[int]]) -> None:
    patient.active_plans = [plan for plan in patient.plans if plan.apply_filters(filters=all_filters)]

def update_lines(patch: Patch, patient: Patient, roi: str, highlight_idxs: dict[str, str]) -> None:
    highlight_idx_list = [int(idx) for idx in highlight_idxs.keys()]
    for plan in patient.plans:
        
        idx = (patient.trace_uids[plan.uid])
        in_highlights = patient.trace_uids[plan.uid] in highlight_idx_list

        if plan not in patient.active_plans and not in_highlights:
            patch["data"][idx]["line"]["color"] = "grey"
            patch["data"][idx]["opacity"] = PASSIVE_OPACITY
            patch["data"][idx]["hoverinfo"] = "skip"
            
        elif not in_highlights:
            patch["data"][idx]["line"]["color"] = plan.dvhs[roi].color
            patch["data"][idx]["opacity"] = ACTIVE_OPACITY
            patch["data"][idx]["hoverinfo"] = "all"
        
        #in highlights
        else:
            patch["data"][idx]["line"]["color"] = highlight_idxs[str(idx)]
            patch["data"][idx]["line"]["width"] = HIGHLIGHT_LINE_WIDTH
            patch["data"][idx]["opacity"] = HIGHLIGHT_OPACITY
            patch["data"][idx][""] = HIGHLIGHT_OPACITY
            patch["data"][idx]["hoverinfo"] = "all"
            if plan not in patient.active_plans:
                patch["data"][idx]["line"]["dash"] = "dot"
            else:
                patch["data"][idx]["line"]["dash"] = None
        
        patch["data"][idx]["hovertemplate"] = plan.hovertemplate+"<br>"+plan.dvhs[roi].hover_info


def update_after_filters_change(patch: Patch, patient: Patient, roi: str, all_filters: dict[str, list[int]], all_metrics: dict[str, dict], highlight_idxs: dict[str, str]) -> Patch:
    
    update_filter_point(patch=patch, patient=patient, roi=roi, all_filters=all_filters)

   #update_scatter(patch=patch, patient=patient, roi=roi)
    update_lines(patch=patch, patient=patient, roi=roi, highlight_idxs=highlight_idxs)

    return patch




def update_after_metrics_change(patch: Patch, patient, roi, all_filters, all_metrics, highlight_idxs):
    metric_type, metric_value = all_metrics[roi]["type"], all_metrics[roi]["value"]
    trace_vline = -1
    trace_hline = -2

    if metric_type == 'D':
        patch["layout"]["shapes"][trace_hline]["visible"] = True
        patch["layout"]["shapes"][trace_vline]["visible"] = False
        patch["layout"]["shapes"][trace_hline]["y0"] = metric_value
        patch["layout"]["shapes"][trace_hline]["y1"] = metric_value
    
    elif metric_type == 'V':
        patch["layout"]["shapes"][trace_hline]["visible"] = False
        patch["layout"]["shapes"][trace_vline]["visible"] = True
        patch["layout"]["shapes"][trace_vline]["x0"] = metric_value
        patch["layout"]["shapes"][trace_vline]["x1"] = metric_value

    elif metric_type == None:
        patch["layout"]["shapes"][trace_vline]["visible"] = False
        patch["layout"]["shapes"][trace_hline]["visible"] = False

    update_lines(patch=patch, patient=patient, roi=roi, highlight_idxs=highlight_idxs)

    

def update_dvh_plots(patient, roi, patch, ctx, all_filters, all_metrics, highlight_idxs) -> Patch:

    trigger = ctx.triggered_id
    
    if trigger == ids.FILTERS:
        update_after_filters_change(
            patch=patch,    
            patient=patient, 
            roi=roi, 
            all_filters=all_filters, 
            all_metrics=all_metrics,
            highlight_idxs=highlight_idxs
            )


        return patch
    
    else:
        update_after_metrics_change(
            patch=patch, 
            patient=patient, 
            roi=roi, 
            all_filters=all_filters, 
            all_metrics=all_metrics,
            highlight_idxs=highlight_idxs
        )

        return patch

