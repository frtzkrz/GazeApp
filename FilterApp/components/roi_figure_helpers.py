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
    dose, vol = roi_filter[roi]
    if trigger == ids.CLEAR_FILTER_BUTTON:
        dose, vol = None, None
        metric_max = None

    elif trigger == ids.APPLY_FILTER_BUTTON:
        if metric_max is not None:
            if metric_type is not None and metric_value is not None:
                if  metric_type == "V":
                    dose, vol = int(metric_value), int(metric_max)
                    roi_filter[roi] = [int(metric_value), int(metric_max)]
                elif metric_type == "D":
                    vol, dose = int(metric_value), int(metric_max)
                    roi_filter[roi] = [int(metric_max), int(metric_value)]

    elif trigger == ids.DVH_PLOT:
        dose, vol = int(dvh_click["points"][0]["x"]), int(dvh_click["points"][0]["y"]) # if dvh_click else roi_filter[roi]

    if dose is not None and vol is not None:
        if dose <= 0: dose = 1
        if dose >= 60: dose = 59
        if vol <= 0: vol = 1
        if vol >= 100: vol = 99

    roi_filter[roi] = [dose, vol]

    return roi_filter, metric_max