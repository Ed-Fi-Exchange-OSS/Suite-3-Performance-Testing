from dataclasses import dataclass


@dataclass
class Measurement:
    resource: str
    URL: str
    page_number: int
    page_size: int
    number_of_records: int
    elapsed_time: int
    http_status_code: int
