from typing import List

from pandas import DataFrame
import pytest

from edfi_paging_test.reporter.paging_measurement import PagingMeasurement
from edfi_paging_test.reporter.paging_request_logger import PaggingRequestLogger


MEASUREMENT_1 = PagingMeasurement(
    "academicWeeks",
    "https://localhost/WebApi/data/v3/",
    1,
    200,
    30,
    40.0,
    200,
)
MEASUREMENT_2 = PagingMeasurement(
    "assignments",
    "https://localhost/WebApi/data/v3/",
    3,
    500,
    500,
    321.0,
    200,
)


def describe_when_logging_a_request() -> None:
    def describe_given_there_is_already_an_item() -> None:
        @pytest.fixture()
        def logs(mocker) -> List[PagingMeasurement]:
            pagingRequestLogger = PaggingRequestLogger()
            pagingRequestLogger.request_log = [MEASUREMENT_1]

            pagingRequestLogger.log_request(
                MEASUREMENT_2.resource,
                MEASUREMENT_2.URL,
                MEASUREMENT_2.page_number,
                MEASUREMENT_2.page_size,
                MEASUREMENT_2.number_of_records,
                MEASUREMENT_2.elapsed_time,
                MEASUREMENT_2.http_status_code
            )

            return pagingRequestLogger.request_log

        def it_appends_new_log_to_end_of_list(logs: List[PagingMeasurement]) -> None:
            assert logs[-1] == MEASUREMENT_2

        def it_leaves_the_original_entry_at_beginning_of_list(
            logs: List[PagingMeasurement],
        ) -> None:
            assert logs[0] == MEASUREMENT_1


def describe_when_converting_to_a_DataFrame() -> None:
    def describe_given_given_an_empty_request_log() -> None:
        def it_raises_a_RuntimeError(mocker) -> None:
            with pytest.raises(RuntimeError):
                PaggingRequestLogger().get_DataFrame()

    def describe_given_two_items() -> None:
        @pytest.fixture()
        def df(mocker) -> DataFrame:
            # Arrange
            paggingRequestLogger = PaggingRequestLogger()
            paggingRequestLogger.request_log = [MEASUREMENT_1, MEASUREMENT_2]

            # Act
            return paggingRequestLogger.get_DataFrame()

        def it_has_two_rows(df: DataFrame) -> None:
            assert df.shape[0] == 2

        def it_has_seven_columns(df: DataFrame) -> None:
            assert df.shape[1] == 7

        @pytest.mark.parametrize(
            "index, expected",
            [(0, MEASUREMENT_1.resource), (1, MEASUREMENT_2.resource)],
        )
        def it_maps_the_resource(df: DataFrame, index: int, expected: str) -> None:
            assert df.iloc[index]["Resource"] == expected

        @pytest.mark.parametrize(
            "index, expected", [(0, MEASUREMENT_1.URL), (1, MEASUREMENT_2.URL)]
        )
        def it_maps_the_url(df: DataFrame, index: int, expected: str) -> None:
            assert df.iloc[index]["URL"] == expected

        @pytest.mark.parametrize(
            "index, expected",
            [(0, MEASUREMENT_1.page_number), (1, MEASUREMENT_2.page_number)],
        )
        def it_maps_the_page_number(df: DataFrame, index: int, expected: str) -> None:
            assert df.iloc[index]["PageNumber"] == expected

        @pytest.mark.parametrize(
            "index, expected",
            [(0, MEASUREMENT_1.page_size), (1, MEASUREMENT_2.page_size)],
        )
        def it_maps_the_page_size(df: DataFrame, index: int, expected: str) -> None:
            assert df.iloc[index]["PageSize"] == expected

        @pytest.mark.parametrize(
            "index, expected",
            [
                (0, MEASUREMENT_1.number_of_records),
                (1, MEASUREMENT_2.number_of_records),
            ],
        )
        def it_maps_the_number_of_records(
            df: DataFrame, index: int, expected: str
        ) -> None:
            assert df.iloc[index]["NumberOfRecords"] == expected

        @pytest.mark.parametrize(
            "index, expected",
            [(0, MEASUREMENT_1.elapsed_time), (1, MEASUREMENT_2.elapsed_time)],
        )
        def it_maps_the_elapsed_time(df: DataFrame, index: int, expected: str) -> None:
            assert df.iloc[index]["ElapsedTime"] == expected

        @pytest.mark.parametrize(
            "index, expected",
            [(0, MEASUREMENT_1.http_status_code), (1, MEASUREMENT_2.http_status_code)],
        )
        def it_maps_the_http_status_code(
            df: DataFrame, index: int, expected: str
        ) -> None:
            assert df.iloc[index]["StatusCode"] == expected
