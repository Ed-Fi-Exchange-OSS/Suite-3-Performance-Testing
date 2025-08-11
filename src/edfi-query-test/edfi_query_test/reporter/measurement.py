from dataclasses import dataclass


@dataclass
class Measurement:
    resource: str
    URL: str
    query_param_count: int
    elapsed_time: float
    http_status_code: int
