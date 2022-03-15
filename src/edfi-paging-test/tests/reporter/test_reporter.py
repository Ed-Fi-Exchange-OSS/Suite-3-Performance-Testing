import pytest
from pandas import DataFrame
import os

from pyfakefs.fake_filesystem import FakeFilesystem, OSType

from edfi_paging_test.reporter.reporter import create_detail_csv


def describe_when_creating_detail_csv() -> None:
    OUTPUT_DIRECTORY = "/output"

    @pytest.fixture(autouse=True)
    def init_fs(fs: FakeFilesystem) -> None:
        # Fake as Linux so that all slashes in these test are forward
        fs.os = OSType.LINUX
        fs.path_separator = "/"
        fs.is_windows_fs = False
        fs.is_macos = False

    def describe_given_a_valid_DataFrame() -> None:

        RUN_NAME = "123"
        EXPECTED_FILE = "/output/123.detail.csv"
        CONTENTS = """Resource,PageNumber,PageSize,NumberOfRecords,ElapsedTime,StatusCode
a,2,3,4,1.3,200
"""

        @pytest.fixture(autouse=True)
        def act():
            df = DataFrame([{
                "Resource": "a",
                "PageNumber": 2,
                "PageSize": 3,
                "NumberOfRecords": 4,
                "ElapsedTime": 1.3,
                "StatusCode": 200
            }])

            create_detail_csv(df, OUTPUT_DIRECTORY, RUN_NAME)

        def it_creates_a_file(fs: FakeFilesystem) -> None:
            assert os.path.exists(EXPECTED_FILE)

        def the_file_has_expected_data(fs: FakeFilesystem) -> None:
            with open(EXPECTED_FILE) as f:
                actual = f.read()

                assert actual == CONTENTS
