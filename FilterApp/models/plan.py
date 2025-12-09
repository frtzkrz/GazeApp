from __future__ import annotations

import numpy as np
from utils.config import *
from models.dvh import DVH
from models.metric import Metric, Filter

from models.model_helpers import get_angle_from_key
class Plan:
    def __init__(
            self,
            patient: Patient, # type: ignore
            angle_key_1: str, 
            dose: np.ndarray,
            two_beam: bool = False, 
            angle_key_2: str | None = None, 
            beam_weight: float | None = None
        ) -> None:

        self.patient_id = patient.patient_id
        self.two_beam = two_beam

        self.angle_key_1 = angle_key_1
        self.polar_1, self.theta_1 = get_angle_from_key(s=self.angle_key_1)

        self.angle_key_2 = angle_key_2
        self.polar_2, self.theta_2 = get_angle_from_key(s=angle_key_2) if self.two_beam else None, None
        self.beam_weight = beam_weight

        self.uid = f"{self.angle_key_1}_{self.angle_key_2}_{self.beam_weight}" if self.two_beam else self.angle_key_1
        
        self.dvhs = {}
        for roi in ROI_NAMES:
            roi_dose = dose[patient.roi_masks[roi]] # type: ignore
            dvh = DVH(
                patient=patient,
                roi_name=roi,
                roi_dose = roi_dose
            )
            self.dvhs[roi] = dvh

        self.visible = True
        if self.two_beam:
            self.hovertemplate = f"{np.round(a=self.beam_weight, decimals=1)}*{self.angle_key_1} + {np.round(a=1-self.beam_weight, decimals=1)}*{self.angle_key_2}" # type: ignore
        else:
            self.hovertemplate = self.angle_key_1

    def __str__(self) -> str:
        res = f"Plan for Patient {self.patient_id}: \n"
        if self.two_beam:
            res += f"{np.round(a=self.beam_weight, decimals=1)}*{self.angle_key_1} + {np.round(a=1-self.beam_weight, decimals=1)}*{self.angle_key_2}" # type: ignore
        else:
            res += self.angle_key_1
        return res
    
    def apply_filter(self, roi: str, f: list[int]) -> bool:
        return self.dvhs[roi].get_dose_at_volume(volume=f[1]) <= f[0]+EPS_FILTER if f[0] is not None and f[1] is not None else True
    
    def apply_filters(self, filters: dict[str, list[int]]) -> bool:
        return all(self.apply_filter(roi=roi, f=filters[roi]) for roi in filters)
    
    def apply_metric(self, metric: Metric) -> None: 
        self.dvhs[metric.roi].set_metric_value(metric=metric)
