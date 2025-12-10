from models.patient import Patient
from utils.config import *  


def update_active_plans(patient: Patient, all_filters: dict[str, list[int]]) -> None:
    patient.active_plans = [plan for plan in patient.plans if plan.apply_filters(filters=all_filters)]

def update_dvh_metrics(patient: Patient, all_metrics: dict[str, dict[str, int | None]]) -> None:
    for plan in patient.plans:
        for roi in ROI_NAMES:
            plan.dvhs[roi].update_metric(metric=all_metrics[roi])
    for roi in ROI_NAMES:
        values = [plan.dvhs[roi].metric_value for plan in patient.plans]
        numeric_values = [v for v in values if v is not None]
        vmin, vmax = min(numeric_values), max(numeric_values)
        colors = [
            str(px.colors.sample_colorscale(COLOR_SCALE, (v - vmin) / (vmax - vmin))[0]) if v is not None else 'grey'
            for v in values
        ]
        for plan, color in zip(patient.plans, colors):
            plan.dvhs[roi].color = color

def update_highlights(patient: Patient, clicks, highlight_idxs: dict[str, str]) ->  dict[str, str]:
    for click in clicks:
        if click is not None:
            angles = click["points"][0]['r'], click["points"][0]['theta']
            uid: str = str(patient.get_plan_uid_from_angles(angles=angles))

            if uid in highlight_idxs:
                del highlight_idxs[uid]
            else:
                highlight_idxs[uid] = next(HIGHLIGHT_COLORS)
    return highlight_idxs