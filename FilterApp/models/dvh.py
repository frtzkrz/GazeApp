from __future__ import annotations
import numpy as np
from models.metric import Metric
from plotly.graph_objs._scatter import Scatter
from utils.config import *

class DVH:
    def __init__(
            self, 
            patient: Patient, # type: ignore
            roi_name: str, 
            roi_dose: np.ndarray,
            bins: int = NUM_POINTS_DVH,
    ) -> None:
        self.roi_name = roi_name
        self.bins = bins

        #define self.dose and self.volume
        self._compute_dvh(patient=patient, roi_dose=roi_dose)

        #compute self.auc
        self.auc = self._get_auc()

        #set metric_value to auc
        self.metric_value = self.auc
        self.metric_title = "AUC"
        
        #precalculate integer D_v and V_d for d integer in (0, 60) Gy and v integer in (0, 100)% 
        self._update_dose_at_integer_volumes()
        self._update_volume_at_integer_doses()

        self.color = None



    
    
    def _compute_dvh(
            self,
            patient: Patient, # type: ignore
            roi_dose: np.ndarray,
    ) -> None:
        
        v = patient.roi_relative_values[self.roi_name] * patient.voxel_vol # type: ignore
        dmin = 0
        dmax = float(roi_dose.max())
        total_vol = np.sum(v)

        # Make bins (edges)
        edges = np.linspace(dmin, dmax, self.bins + 1)
        
        # differential DVH: sum volumes per dose bin
        bin_idx = np.searchsorted(edges, roi_dose, side='right') - 1

        # clamp indices
        bin_idx = np.clip(bin_idx, 0, self.bins-1)
        diff = np.bincount(bin_idx, weights=v, minlength=self.bins)  # volumes per bin

        # cumulative DVH (volume >= D) — compute from the top
        # create center points for bins (optional)
        dose = 0.5 * (edges[:-1] + edges[1:])
        # cumulative from high dose to low dose:
        vol = np.cumsum(diff[::-1])[::-1]/total_vol*100

        self.dose = dose
        self.volume = vol


    def _get_volume_at_dose(self, dose):
        """
        Return Vx: the volume (%) receiving at least dose.
        dvh_dose, dvh_volume can be ascending or descending; handles both.
        """
        # Ensure numpy arrays
        dvh_dose = np.asarray(self.dose)
        dvh_volume = np.asarray(self.volume)
        
        # Make sure dose is ascending for interpolation
        if dvh_dose[0] > dvh_dose[-1]:
            dvh_dose = dvh_dose[::-1]
            dvh_volume = dvh_volume[::-1]
        
        # Interpolate volume at dose x
        return np.interp(dose, dvh_dose, dvh_volume)

    def _get_dose_at_volume(self, volume):
        """#
        Return Dx: the dose corresponding to volume x.
        - x can be scalar or array (volume units).
        - If clip=True (default), x outside the range of `volume` is clipped to min/max.
        If clip=False, np.interp will extrapolate using end values (which is usually undesirable).
        Assumes `volume` is cumulative DVH (monotonic, typically decreasing with dose).
        """
        dvh_dose = np.asarray(self.dose)
        dvh_volume = np.asarray(self.volume)

        # np.interp requires the xp (here: volume) to be ascending.
        # If volume is descending, reverse both arrays to make volume ascending.
        if dvh_volume[0] > dvh_volume[-1]:
            dvh_dose = dvh_dose[::-1]
            dvh_volume = dvh_volume[::-1]
        volume = np.asarray(volume)
        volume = np.clip(volume, dvh_volume.min(), dvh_volume.max())
        # interpolate dose as a function of volume (xp=volume, fp=dose)
        return np.interp(volume, dvh_volume, dvh_dose)

    def _update_dose_at_integer_volumes(self):
        self.dose_at_integer_volumes = {int(i): float(self._get_dose_at_volume(volume=i)) for i in np.arange(start=1, stop=100)}
    
    
    def _update_volume_at_integer_doses(self):
        self.volume_at_integer_dose = {int(i): float(self._get_volume_at_dose(dose=i)) for i in np.arange(start=1, stop=60)}

    def _get_auc(self) -> float:
        return np.trapezoid(y=self.volume, x=self.dose)

    def get_dose_at_volume(self, volume) -> float:
        return self.dose_at_integer_volumes[int(volume)]

    def get_volume_at_dose(self, dose) -> float:
        return self.volume_at_integer_dose[int(dose)]
    
    def get_metric(self, metric: Metric) -> float:
        if metric.metric_type == 'D':
            return self.get_dose_at_volume(metric.metric_value)
        else:
            return self.get_volume_at_dose(dose=metric.metric_value)

    def set_metric_value(self, metric: Metric) -> float:
        self.metric_value = self.get_metric(metric=metric)
        return self.metric_value


    #def plot(self) -> _scatter.Scatter
    
