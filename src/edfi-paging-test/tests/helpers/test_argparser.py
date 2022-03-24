# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import os
from typing import List
import sys

import pytest

from edfi_paging_test.helpers.argparser import MainArguments, parse_main_arguments
from edfi_paging_test.helpers.output_format import OutputFormat
from edfi_paging_test.helpers.log_level import LogLevel


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
    def describe_given_full_set_of_arguments() -> None:
        @pytest.fixture()
        def main_arguments() -> MainArguments:
            sys.argv = [
                "pytest",
                "-b", "http://api.ed-fi.org/v5.1",
                "-k", "populatedTemplateX",
                "-s", "populatedSecretX",
                "-c", "404",
                "-o", "test_outputX",
                "-t", str(OutputFormat.CSV),
                "-r", "academicWeeks", "students",
                "-p", "42",
                "-l", "debug",
                "-d", "test run"
            ]

            return parse_main_arguments()

        def it_sets_base_url(main_arguments: MainArguments) -> None:
            assert main_arguments.baseUrl == "http://api.ed-fi.org/v5.1"

        def it_sets_api_key(main_arguments: MainArguments) -> None:
            assert main_arguments.key == "populatedTemplateX"

        def it_sets_api_secret(main_arguments: MainArguments) -> None:
            assert main_arguments.secret == "populatedSecretX"

        def it_sets_connection_limit(main_arguments: MainArguments) -> None:
            assert main_arguments.connectionLimit == 404

        def it_sets_output_dir(main_arguments: MainArguments) -> None:
            assert main_arguments.output == "test_outputX"

        def it_sets_content_type(main_arguments: MainArguments) -> None:
            assert main_arguments.contentType == OutputFormat.CSV

        def it_sets_resource_list(main_arguments: MainArguments) -> None:
            assert main_arguments.resourceList == ["academicWeeks", "students"]

        def it_sets_page_size(main_arguments: MainArguments) -> None:
            assert main_arguments.pageSize == 42

        def it_sets_log_level(main_arguments: MainArguments) -> None:
            assert main_arguments.log_level == LogLevel.DEBUG

        def it_sets_description(main_arguments: MainArguments) -> None:
            assert main_arguments.description == "test run"

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
        os.environ["PERF_CONTENT_TYPE"] = str(OutputFormat.JSON)
        os.environ["PERF_RESOURCE_LIST"] = '["a", "b"]'
        os.environ["PERF_API_PAGE_SIZE"] = "402"
        os.environ["PERF_LOG_LEVEL"] = "WARNing"
        os.environ["PERF_DESCRIPTION"] = "page run"

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
        assert main_arguments.contentType == OutputFormat.JSON

    def it_sets_resource_list(main_arguments: MainArguments) -> None:
        assert main_arguments.resourceList == ["a", "b"]

    def it_sets_page_size(main_arguments: MainArguments) -> None:
        assert main_arguments.pageSize == 402

    def it_sets_log_level(main_arguments: MainArguments) -> None:
        assert main_arguments.log_level == LogLevel.WARNING

    def it_sets_description(main_arguments: MainArguments) -> None:
        assert main_arguments.description == "page run"
