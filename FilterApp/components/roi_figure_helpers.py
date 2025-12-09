from dataclasses import dataclass
from . import ids
from typing import Any
from dash import Patch
from models.patient import Patient
from utils.config import *

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

def update_filter_points(patch: Patch, patient: Patient, roi: str, all_filters: dict[str, list[int]]) -> None:
    idx = patient.trace_uids["filter-point"]
    if all_filters[roi] == [None, None]:
        patch["data"][idx]["visible"] = False
    else:
        patch["data"][idx]["visible"] = True
        patch["data"][idx]["x"] = [all_filters[roi][0]]
        patch["data"][idx]["y"] = [all_filters[roi][1]]

def update_active_plans(patient: Patient, all_filters: dict[str, list[int]]) -> None:
    print("Recalculating active plans...")
    patient.active_plans = [plan for plan in patient.plans if plan.apply_filters(filters=all_filters)]
    print(f"Number of active plans: {len(patient.active_plans)}")

def update_lines(patch: Patch, patient: Patient, roi: str) -> None:
    for plan in patient.plans:
        idx = patient.trace_uids[plan.uid]
        if plan not in patient.active_plans:
            patch["data"][idx]["line"]["color"] = "grey"
            patch["data"][idx]["opacity"] = PASSIVE_OPACITY
        
        else:
            patch["data"][idx]["line"]["color"] = plan.dvhs[roi].color
            patch["data"][idx]["opacity"] = ACTIVE_OPACITY

def update_after_filters_change(patch: Patch, patient: Patient, roi: str, all_filters: dict[str, list[int]], all_metrics: dict[str, dict]) -> Patch:
    
    #patch filter point
    update_filter_points(patch=patch, patient=patient, roi=roi, all_filters=all_filters)

    #update_active_plans(patient=patient, all_filters=all_filters)

    update_lines(patch=patch, patient=patient, roi=roi)
    #filter plans
    #filter_plans()

    #adjust colors






    #patch lines
    
    
    
    return patch







def update_after_metrics_change(patch: Patch, patient, roi, all_filters, all_metrics):
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