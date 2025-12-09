import numpy as np
import h5py
from utils.config import *
from models.plan import Plan
from models.metric import Filter, Metric

class Patient:
    def __init__(
            self,
            patient_id: str,
            h5_file: h5py.File,
    ) -> None:      
        
        self.patient_id = patient_id
        mask_datasets = {roi_name: h5_file[f'{roi_name}_mask'] for roi_name in ROI_NAMES}
        self.roi_masks = {roi_name: mask_datasets[roi_name] for roi_name in ROI_NAMES}

        f_keys = h5_file.keys()
        self.angle_keys: list[str] = [key for key in f_keys if '(' in key]

        relative_dataset = {roi_name: h5_file[f'{roi_name}_relative_volumes'] for roi_name in ROI_NAMES}
        self.roi_relative_values = {roi_name: relative_dataset[roi_name] for roi_name in ROI_NAMES}

        self.voxel_vol = h5_file.attrs['voxel_volume']

        self.plans: list[Plan] = []
        self.plans_single_beam: list[Plan] = []

        self.filters: dict[str, Filter] = {}

        self.metrics: dict[str, Metric] = {}

        self.trace_uids = {}
        
    
    def __str__(self) -> str:
        return f"Patient {self.patient_id} with {len(self.angle_keys)} gaze angles and {len(self.plans)} plans."
    
    def add_plans(
            self,
            h5_file: h5py.File,
            two_beam: bool = False,
            n_weights: int = 1,
            
    ) -> None:
        """
        Add plans to patient
        
        :param self: Patient
        :param two_beam: True if two beam plans should be calculated, else false (Default: False)
        :type two_beam: bool
        :param n_weights: Number of equally spaced beam weights between 0 and 1 for beam angle 1. (Default: 1, so only equally weighted plans)
        :type n_weights: int
        """
        if two_beam: self.plans_two_beam = []

        for i, angle_key_1 in enumerate(self.angle_keys):
            dose_1 = h5_file[angle_key_1][:] # type: ignore

            #add single beam plans to patient.plans
            plan = Plan(
                patient=self,
                angle_key_1=angle_key_1,
                dose=dose_1, # type: ignore
            )
            self.plans_single_beam.append(plan)

            if two_beam:
                
                print(f"Calculating plans: {i}/{len(self.angle_keys)}", end='\r')

                for angle_key_2 in self.angle_keys[i+1:]:
                    if angle_key_1 == angle_key_2: print("Stop")
                    dose_2 = h5_file[angle_key_2][:] # type: ignore

                    for weight in np.linspace(start=0, stop=1, num=n_weights+1, endpoint=False)[1:]:
                        dose = weight*dose_1 + (1-weight)*dose_2
                        plan = Plan(
                            patient=self,
                            angle_key_1=angle_key_1,
                            angle_key_2=angle_key_2,
                            dose=dose,
                            two_beam=True,
                            beam_weight=weight
                        )
                        self.plans_two_beam.append(plan)
        

        self.plans = self.plans_single_beam.copy()
        
        if two_beam: self.plans += self.plans_two_beam
    
        self.active_plans=self.plans.copy()

        self.metrics = {}

    def apply_filters(self) -> None: #Only to be called when new filter is added
        self.active_plans = [p for p in self.plans if p.apply_filters(filters=self.filters)]
        self.passive_plans = [p for p in self.plans if p not in self.active_plans]

    def add_filter(self, f: Filter) -> None:

        self.filters[f.metric.roi] = f

        #recalculate active and passive plans
        self.apply_filters()
    
    def remove_filter(self, roi: str) -> None:
        if roi in self.filters:

            del self.filters[roi]

            #recalculate active and passive plans
            self.apply_filters()
    
    def apply_metric(self, metric: Metric) -> None:
        [plan.apply_metric(metric=metric) for plan in self.plans]
    
