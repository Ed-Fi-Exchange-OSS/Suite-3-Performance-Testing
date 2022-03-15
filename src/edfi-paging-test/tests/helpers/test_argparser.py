# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import os
from typing import List
import sys

import pytest

from edfi_paging_test.helpers.argparser import MainArguments, parse_main_arguments


BASEURL = "http://localhost:54746"
KEY = "empty"
SECRET = "emptySecret"


def _baseUrl_args() -> List[str]:
    return ["--baseUrl", BASEURL]


def _key_args() -> List[str]:
    return ["--key", KEY]


def _secret_args() -> List[str]:
    return ["--secret", SECRET]


def _assert_no_messages(capsys) -> None:
    out, err = capsys.readouterr()

    assert err == "", "There should be an error message"
    assert out == "", "There should not be an output message"


def _assert_error_message(capsys) -> None:
    out, err = capsys.readouterr()

    assert err != "", "There should be an error message"
    assert out == "", "There should not be an output message"


def describe_when_parsing_from_command_line_args() -> None:
    def describe_given_arguments_do_not_include_baseUrl() -> None:
        def it_should_show_help(capsys) -> None:
            with pytest.raises(SystemExit):
                sys.argv = [
                    "pytest",
                    *_key_args(),
                    *_secret_args(),
                ]

                parse_main_arguments()
                _assert_error_message(capsys)

    def describe_given_arguments_do_not_include_key() -> None:
        def it_should_show_help(capsys) -> None:
            with pytest.raises(SystemExit):
                sys.argv = [
                    "pytest",
                    *_baseUrl_args(),
                    *_secret_args(),
                ]

                parse_main_arguments()
                _assert_error_message(capsys)

    def describe_given_arguments_do_not_include_secret() -> None:
        def it_should_show_help(capsys) -> None:
            with pytest.raises(SystemExit):
                sys.argv = [
                    "pytest",
                    *_baseUrl_args(),
                    *_key_args(),
                ]

                parse_main_arguments()
                _assert_error_message(capsys)


def describe_when_parsing_from_env_vars() -> None:
    @pytest.fixture()
    def main_arguments() -> MainArguments:
        os.environ["PERF_API_BASEURL"] = "http://api.ed-fi.org"
        os.environ["PERF_API_KEY"] = "populatedTemplate"
        os.environ["PERF_API_SECRET"] = "populatedSecret"
        os.environ["PERF_CONNECTION_LIMIT"] = "40"
        os.environ["PERF_OUTPUT_DIR"] = "test_output"
        os.environ["PERF_CONTENT_TYPE"] = "JSON"
        os.environ["PERF_RESOURCE_LIST"] = '["a", "b"]'
        os.environ["PERF_API_PAGE_SIZE"] = "402"

        sys.argv = ["pytest"]

        return parse_main_arguments()

    def it_sets_base_url(main_arguments: MainArguments) -> None:
        assert main_arguments.baseUrl == "http://api.ed-fi.org"

    def it_sets_api_key(main_arguments: MainArguments) -> None:
        assert main_arguments.key == "populatedTemplate"

    def it_sets_api_secret(main_arguments: MainArguments) -> None:
        assert main_arguments.secret == "populatedSecret"

    def it_sets_connection_limit(main_arguments: MainArguments) -> None:
        assert main_arguments.connectionLimit == 40

    def it_sets_output_dir(main_arguments: MainArguments) -> None:
        assert main_arguments.output == "test_output"

    def it_sets_content_type(main_arguments: MainArguments) -> None:
        assert main_arguments.contentType == "JSON"

    def it_sets_resource_list(main_arguments: MainArguments) -> None:
        assert main_arguments.resourceList == ["a", "b"]

    def it_sets_page_size(main_arguments: MainArguments) -> None:
        assert main_arguments.pageSize == 402
