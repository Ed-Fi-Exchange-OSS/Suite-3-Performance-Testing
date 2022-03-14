from typing import List

from pandas import DataFrame
import pytest

from edfi_paging_test.helpers.measurement import Measurement


def describe_given_when_converting_to_a_DataFrame() -> None:
    MEASUREMENT_1 = Measurement(
        "academicWeeks",
        "https://localhost/WebApi/data/v3/ed-fi/academicWeeks",
        1,
        200,
        30,
        40,
        200,
    )
    MEASUREMENT_2 = Measurement(
        "assignments",
        "https://localhost/WebApi/data/v3/lmsx/assignments",
        3,
        500,
        500,
        321,
        200,
    )

    def describe_given_given_an_empty_list() -> None:
        def it_raises_a_ValueError() -> None:
            with pytest.raises(ValueError):
                Measurement.to_DataFrame(list())

    def describe_given_two_items() -> None:
        @pytest.fixture()
        def df() -> DataFrame:
            return Measurement.to_DataFrame([MEASUREMENT_1, MEASUREMENT_2])

        def it_has_two_rows(df: DataFrame) -> None:
            assert df.shape[0] == 2

        def it_has_seven_columns(df: DataFrame) -> None:
            assert df.shape[1] == 7

        @pytest.mark.parametrize(
            "index, expected",
            [(0, MEASUREMENT_1.resource), (1, MEASUREMENT_2.resource)],
        )
        def it_maps_the_resource(df: DataFrame, index: int, expected: str) -> None:
            assert df.loc[index, "Resource"] == expected

        @pytest.mark.parametrize(
            "index, expected", [(0, MEASUREMENT_1.URL), (1, MEASUREMENT_2.URL)]
        )
        def it_maps_the_url(df: DataFrame, index: int, expected: str) -> None:
            assert df.loc[index, "URL"] == expected

        @pytest.mark.parametrize(
            "index, expected",
            [(0, MEASUREMENT_1.page_number), (1, MEASUREMENT_2.page_number)],
        )
        def it_maps_the_page_number(df: DataFrame, index: int, expected: str) -> None:
            assert df.loc[index, "PageNumber"] == expected

        @pytest.mark.parametrize(
            "index, expected",
            [(0, MEASUREMENT_1.page_size), (1, MEASUREMENT_2.page_size)],
        )
        def it_maps_the_page_size(df: DataFrame, index: int, expected: str) -> None:
            assert df.loc[index, "PageSize"] == expected

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
            assert df.loc[index, "NumberOfRecords"] == expected

        @pytest.mark.parametrize(
            "index, expected",
            [(0, MEASUREMENT_1.elapsed_time), (1, MEASUREMENT_2.elapsed_time)],
        )
        def it_maps_the_elapsed_time(df: DataFrame, index: int, expected: str) -> None:
            assert df.loc[index, "ElapsedTime"] == expected

        @pytest.mark.parametrize(
            "index, expected",
            [(0, MEASUREMENT_1.http_status_code), (1, MEASUREMENT_2.http_status_code)],
        )
        def it_maps_the_http_status_code(
            df: DataFrame, index: int, expected: str
        ) -> None:
            assert df.loc[index, "StatusCode"] == expected
