from dataclasses import dataclass
from utils.config import *


@dataclass
class Metric:
    roi: str
    metric_type: str
    metric_value: float

    def __post_init__(self) -> None:
        if self.metric_type not in ('D', 'V'):
            raise ValueError(f"metric_type must be 'D' or 'V', got {self.metric_type}")

        if self.roi not in ROI_NAMES:
            raise ValueError(f"Given ROI not in ROI_NAMES, got {self.roi}")
        
        self.name = f"{self.metric_type}{self.metric_value}_{self.roi}"

    def __str__(self) -> str:
        return self.name


@dataclass
class Filter:
    metric: Metric
    max: float


    def __str__(self) -> str:
        return f"{self.metric.name} < {self.max}"
