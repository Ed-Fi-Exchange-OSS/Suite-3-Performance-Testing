from dataclasses import dataclass


@dataclass
class FilteredReadMeasurement:
    resource: str
    URL: str
    filter_count: int
    elapsed_time: float
    http_status_code: int
