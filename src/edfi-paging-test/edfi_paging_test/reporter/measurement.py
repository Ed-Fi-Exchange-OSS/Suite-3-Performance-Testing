from dataclasses import dataclass
from typing import Callable, Tuple, TypeVar
import timeit

T = TypeVar("T")


@dataclass
class Measurement:
    resource: str
    URL: str
    page_number: int
    page_size: int
    number_of_records: int
    elapsed_time: float
    http_status_code: int

    @staticmethod
    def timeit(callback: Callable[[], T]) -> Tuple[float, T]:
        start = timeit.default_timer()

        response = callback()

        elapsed = timeit.default_timer() - start

        return (elapsed, response)
