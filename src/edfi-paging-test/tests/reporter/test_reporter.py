import pytest
import re
from pandas import DataFrame, read_csv, read_json
from os import path
from edfi_paging_test.reporter.summary import Summary
from edfi_paging_test.helpers.main_arguments import MainArguments
from edfi_paging_test.helpers.log_level import LogLevel
from edfi_paging_test.helpers.output_format import OutputFormat
from pyfakefs.fake_filesystem import FakeFilesystem, OSType  # type: ignore

from edfi_paging_test.reporter.reporter import (
    create_detail_csv,
    create_statistics_csv,
    create_detail_json,
    create_statistics_json,
    create_summary_json,
)
from edfi_paging_test.reporter.paging_request_logger import PaggingRequestLogger
from edfi_paging_test.helpers.test_type import TestType


def describe_when_creating_detail_csv() -> None:
    @pytest.fixture(autouse=True)
    def init_fs(fs: FakeFilesystem) -> None:
        # Fake as Linux so that all slashes in these test are forward
        fs.os = OSType.LINUX
        fs.path_separator = "/"
        fs.is_windows_fs = False
        fs.is_macos = False

    def describe_given_a_valid_DataFrame() -> None:
        OUTPUT_DIRECTORY = "/output"
        RUN_NAME = "123"
        EXPECTED_FILE = "/output/123/detail.csv"
        CONTENTS = """Resource,PageNumber,PageSize,NumberOfRecords,ElapsedTime,StatusCode
a,2,3,4,1.3,200
"""

        @pytest.fixture(autouse=True)
        def act():
            df = DataFrame(
                [
                    {
                        "Resource": "a",
                        "PageNumber": 2,
                        "PageSize": 3,
                        "NumberOfRecords": 4,
                        "ElapsedTime": 1.3,
                        "StatusCode": 200,
                    }
                ]
            )

            create_detail_csv(df, OUTPUT_DIRECTORY, RUN_NAME)

        def it_creates_a_file(fs: FakeFilesystem) -> None:
            assert path.exists(EXPECTED_FILE)

        def the_file_has_expected_data(fs: FakeFilesystem) -> None:
            with open(EXPECTED_FILE) as f:
                actual = f.read()

                assert actual == CONTENTS


def describe_when_creating_statistics_csv() -> None:
    OUTPUT_DIRECTORY = "/output"
    RUN_NAME = "1243"
    EXPECTED_FILE = "/output/1243/statistics.csv"

    @pytest.fixture(autouse=True)
    def init_fs(fs: FakeFilesystem) -> None:
        # Fake as Linux so that all slashes in these test are forward
        fs.os = OSType.LINUX
        fs.path_separator = "/"
        fs.is_windows_fs = False
        fs.is_macos = False

        # Pre-create the output path, whereas it was not created before running
        # the detail file test above.
        fs.create_dir(path.join(OUTPUT_DIRECTORY, RUN_NAME))  # type: ignore

    def describe_given_a_valid_DataFrame() -> None:
        @pytest.fixture(autouse=True)
        def act(mocker):
            df = DataFrame(
                [
                    {
                        "Resource": "a",
                        "PageNumber": 1,
                        "PageSize": 3,
                        "NumberOfRecords": 3,
                        "ElapsedTime": 1.3,
                        "StatusCode": 200,
                    },
                    {
                        "Resource": "a",
                        "PageNumber": 2,
                        "PageSize": 3,
                        "NumberOfRecords": 3,
                        "ElapsedTime": 1.21,
                        "StatusCode": 200,
                    },
                    {
                        "Resource": "a",
                        "PageNumber": 3,
                        "PageSize": 3,
                        "NumberOfRecords": 0,
                        "ElapsedTime": 2.21,
                        "StatusCode": 500,
                    },
                    {
                        "Resource": "a",
                        "PageNumber": 3,
                        "PageSize": 3,
                        "NumberOfRecords": 2,
                        "ElapsedTime": 1.01,
                        "StatusCode": 200,
                    },
                    {
                        "Resource": "b",
                        "PageNumber": 1,
                        "PageSize": 500,
                        "NumberOfRecords": 500,
                        "ElapsedTime": 2.3323,
                        "StatusCode": 200,
                    },
                    {
                        "Resource": "b",
                        "PageNumber": 2,
                        "PageSize": 500,
                        "NumberOfRecords": 499,
                        "ElapsedTime": 2.0323,
                        "StatusCode": 200,
                    },
                    {
                        "Resource": "b",
                        "PageNumber": 1,
                        # Different page size, therefore will be treated as a different resource
                        "PageSize": 10,
                        "NumberOfRecords": 40,
                        "ElapsedTime": 1.532,
                        "StatusCode": 200,
                    },
                ]
            )

            pagingRequestLogger = PaggingRequestLogger()
            mocker.patch.object(pagingRequestLogger, 'get_DataFrame', return_value=df)

            create_statistics_csv(pagingRequestLogger.get_statistics(), OUTPUT_DIRECTORY, RUN_NAME)

        def it_creates_the_file(fs) -> None:
            assert fs.exists(EXPECTED_FILE)

        @pytest.fixture
        def file(fs) -> DataFrame:
            return read_csv(EXPECTED_FILE)

        @pytest.mark.parametrize(
            "field, value",
            [
                ("Resource", "a"),
                ("PageSize", 3),
                ("NumberOfPages", 3),
                ("NumberOfRecords", 8),
                ("TotalTime", 5.73),
                ("MeanTime", 1.4325),
                ("StDeviation", 0.532314),
                ("NumberOfErrors", 1),
            ],
        )
        def it_creates_the_correct_record_for_resource_a(
            file: DataFrame, field, value
        ) -> None:
            assert file.shape[0] == 3

            query = file[(file.Resource == "a")][field]
            assert query.iloc[0] == value

        @pytest.mark.parametrize(
            "field, value",
            [
                ("Resource", "b"),
                ("PageSize", 500),
                ("NumberOfPages", 2),
                ("NumberOfRecords", 999),
                ("TotalTime", 4.3646),
                ("MeanTime", 2.1823),
                ("StDeviation", 0.212132),
                ("NumberOfErrors", 0),
            ],
        )
        def it_creates_the_correct_record_for_resource_b_500(
            file: DataFrame, field, value
        ) -> None:
            assert file.shape[0] == 3

            query = file[(file.Resource == "b") & (file.PageSize == 500)][field]

            assert query.iloc[0] == value

        @pytest.mark.parametrize(
            "field, value",
            [
                ("Resource", "b"),
                ("PageSize", 10),
                ("NumberOfPages", 1),
                ("NumberOfRecords", 40),
                ("TotalTime", 1.532),
                ("MeanTime", 1.532),
                ("StDeviation", 0),
                ("NumberOfErrors", 0),
            ],
        )
        def it_creates_the_correct_record_for_resource_b_10(
            file: DataFrame, field, value
        ) -> None:
            assert file.shape[0] == 3

            query = file[(file.Resource == "b") & (file.PageSize == 10)][field]
            assert query.iloc[0] == value


def describe_when_creating_detail_json() -> None:
    @pytest.fixture(autouse=True)
    def init_fs(fs: FakeFilesystem) -> None:
        # Fake as Linux so that all slashes in these test are forward
        fs.os = OSType.LINUX
        fs.path_separator = "/"
        fs.is_windows_fs = False
        fs.is_macos = False

    def describe_given_a_valid_DataFrame() -> None:
        OUTPUT_DIRECTORY = "/output"
        RUN_NAME = "123"
        EXPECTED_FILE = "/output/123/detail.json"
        CONTENTS = '[{"Resource":"a","PageNumber":2,"PageSize":3,"NumberOfRecords":4,"ElapsedTime":1.3,"StatusCode":200}]'

        @pytest.fixture(autouse=True)
        def act():
            df = DataFrame(
                [
                    {
                        "Resource": "a",
                        "PageNumber": 2,
                        "PageSize": 3,
                        "NumberOfRecords": 4,
                        "ElapsedTime": 1.3,
                        "StatusCode": 200,
                    }
                ]
            )

            create_detail_json(df, OUTPUT_DIRECTORY, RUN_NAME)

        def it_creates_a_file(fs: FakeFilesystem) -> None:
            assert path.exists(EXPECTED_FILE)

        def the_file_has_expected_data(fs: FakeFilesystem) -> None:
            with open(EXPECTED_FILE) as f:
                actual = f.read()

                assert actual == CONTENTS


def describe_when_creating_statistics_json() -> None:
    OUTPUT_DIRECTORY = "/output"
    RUN_NAME = "1243"
    EXPECTED_FILE = "/output/1243/statistics.json"

    @pytest.fixture(autouse=True)
    def init_fs(fs: FakeFilesystem) -> None:
        # Fake as Linux so that all slashes in these test are forward
        fs.os = OSType.LINUX
        fs.path_separator = "/"
        fs.is_windows_fs = False
        fs.is_macos = False

        # Pre-create the output path, whereas it was not created before running
        # the detail file test above.
        fs.create_dir(path.join(OUTPUT_DIRECTORY, RUN_NAME))  # type: ignore

    def describe_given_a_valid_DataFrame() -> None:
        @pytest.fixture(autouse=True)
        def act(mocker):
            df = DataFrame(
                [
                    {
                        "Resource": "a",
                        "PageNumber": 1,
                        "PageSize": 3,
                        "NumberOfRecords": 3,
                        "ElapsedTime": 1.3,
                        "StatusCode": 200,
                    },
                    {
                        "Resource": "a",
                        "PageNumber": 2,
                        "PageSize": 3,
                        "NumberOfRecords": 3,
                        "ElapsedTime": 1.21,
                        "StatusCode": 200,
                    },
                    {
                        "Resource": "a",
                        "PageNumber": 3,
                        "PageSize": 3,
                        "NumberOfRecords": 0,
                        "ElapsedTime": 2.21,
                        "StatusCode": 500,
                    },
                    {
                        "Resource": "a",
                        "PageNumber": 3,
                        "PageSize": 3,
                        "NumberOfRecords": 2,
                        "ElapsedTime": 1.01,
                        "StatusCode": 200,
                    },
                    {
                        "Resource": "b",
                        "PageNumber": 1,
                        "PageSize": 500,
                        "NumberOfRecords": 500,
                        "ElapsedTime": 2.3323,
                        "StatusCode": 200,
                    },
                    {
                        "Resource": "b",
                        "PageNumber": 2,
                        "PageSize": 500,
                        "NumberOfRecords": 499,
                        "ElapsedTime": 2.0323,
                        "StatusCode": 200,
                    },
                    {
                        "Resource": "b",
                        "PageNumber": 1,
                        # Different page size, therefore will be treated as a different resource
                        "PageSize": 10,
                        "NumberOfRecords": 40,
                        "ElapsedTime": 1.532,
                        "StatusCode": 200,
                    },
                ]
            )

            pagingRequestLogger = PaggingRequestLogger()
            mocker.patch.object(pagingRequestLogger, 'get_DataFrame', return_value=df)

            create_statistics_json(pagingRequestLogger.get_statistics(), OUTPUT_DIRECTORY, RUN_NAME)

        def it_creates_the_file(fs) -> None:
            assert fs.exists(EXPECTED_FILE)

        @pytest.fixture
        def file(fs) -> DataFrame:
            return read_json(EXPECTED_FILE)  # type: ignore

        @pytest.mark.parametrize(
            "field, value",
            [
                ("Resource", "a"),
                ("PageSize", 3),
                ("NumberOfPages", 3),
                ("NumberOfRecords", 8),
                ("TotalTime", 5.73),
                ("MeanTime", 1.4325),
                ("StDeviation", 0.532314),
                ("NumberOfErrors", 1),
            ],
        )
        def it_creates_the_correct_record_for_resource_a(
            file: DataFrame, field, value
        ) -> None:
            assert file.shape[0] == 3

            query = file[(file.Resource == "a")][field]
            assert query.iloc[0] == value

        @pytest.mark.parametrize(
            "field, value",
            [
                ("Resource", "b"),
                ("PageSize", 500),
                ("NumberOfPages", 2),
                ("NumberOfRecords", 999),
                ("TotalTime", 4.3646),
                ("MeanTime", 2.1823),
                ("StDeviation", 0.212132),
                ("NumberOfErrors", 0),
            ],
        )
        def it_creates_the_correct_record_for_resource_b_500(
            file: DataFrame, field, value
        ) -> None:
            assert file.shape[0] == 3

            query = file[(file.Resource == "b") & (file.PageSize == 500)][field]

            assert query.iloc[0] == value

        @pytest.mark.parametrize(
            "field, value",
            [
                ("Resource", "b"),
                ("PageSize", 10),
                ("NumberOfPages", 1),
                ("NumberOfRecords", 40),
                ("TotalTime", 1.532),
                ("MeanTime", 1.532),
                ("StDeviation", 0),
                ("NumberOfErrors", 0),
            ],
        )
        def it_creates_the_correct_record_for_resource_b_10(
            file: DataFrame, field, value
        ) -> None:
            assert file.shape[0] == 3

            query = file[(file.Resource == "b") & (file.PageSize == 10)][field]
            assert query.iloc[0] == value


def describe_when_creating_summary_json() -> None:
    @pytest.fixture(autouse=True)
    def init_fs(fs: FakeFilesystem) -> None:
        # Fake as Linux so that all slashes in these test are forward
        fs.os = OSType.LINUX
        fs.path_separator = "/"
        fs.is_windows_fs = False
        fs.is_macos = False

    def describe_given_a_valid_DataFrame() -> None:
        OUTPUT_DIRECTORY = "/output"
        RUN_NAME = "123"
        EXPECTED_FILE = "/output/123/summary.json"
        CONTENTS = """[{
            "RunName":"123",
            "MachineName":"MyMachine",
            "RunConfigration.Baseurl":"testhost",
            "RunConfigration.Connectionlimit":4,
            "RunConfigration.Key":"populatedTemplateX",
            "RunConfigration.Secret":"populatedSecretX",
            "RunConfigration.Ignorecertificateerrors":true,
            "RunConfigration.Output":"test_outputX",
            "RunConfigration.Description":"test",
            "RunConfigration.Contenttype":"CSV",
            "RunConfigration.Resourcelist":["a","b"],
            "RunConfigration.Pagesize":100,
            "RunConfigration.LogLevel":"DEBUG",
            "RunConfigration.TestType":"DEEP_PAGING",
            "RunConfigration.CombinationSizeLimit":1
            }]"""

        @pytest.fixture(autouse=True)
        def act():

            summary = Summary(
                run_name=RUN_NAME,
                machine_name="MyMachine",
                run_configration=MainArguments(
                    "testhost",
                    4,
                    "populatedTemplateX",
                    "populatedSecretX",
                    True,
                    "test_outputX",
                    "test",
                    OutputFormat.CSV,
                    ["a", "b"],
                    100,
                    LogLevel.DEBUG,
                    TestType.DEEP_PAGING,
                    1
                )
            )
            df = summary.get_DataFrame()
            create_summary_json(df, OUTPUT_DIRECTORY, RUN_NAME)

        def it_creates_a_file(fs: FakeFilesystem) -> None:
            assert path.exists(EXPECTED_FILE)

        def the_file_has_expected_data(fs: FakeFilesystem) -> None:
            with open(EXPECTED_FILE) as f:
                actual = f.read()

                assert actual == re.sub('\\s+', '', CONTENTS)
