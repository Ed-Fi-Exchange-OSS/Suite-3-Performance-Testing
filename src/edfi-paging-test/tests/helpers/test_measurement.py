from time import sleep
from typing import Tuple

import pytest

from edfi_paging_test.helpers.measurement import Measurement

SLEEP_TIME = 0.1


def describe_when_timing_a_callback():
    def describe_given_asdfasdf():
        RESPONSE = {"a": "b"}

        def callback() -> dict:
            sleep(SLEEP_TIME)
            return RESPONSE

        @pytest.fixture
        def time_response() -> Tuple[float, dict]:
            return Measurement.timeit(callback)

        def it_returns_measured_time(time_response: Tuple[float, dict]):
            assert time_response[0] > SLEEP_TIME
            # Just confirm it is very close to the sleep time.
            assert time_response[0] < SLEEP_TIME*1.1

        def it_returns_callback_response(time_response: Tuple[float, dict]):
            assert time_response[1] == RESPONSE
