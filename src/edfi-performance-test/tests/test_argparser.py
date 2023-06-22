# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import os
from typing import List
import sys

import pytest

from edfi_performance_test.helpers.argparser import parse_main_arguments
from edfi_performance_test.helpers.main_arguments import MainArguments
from edfi_performance_test.helpers.log_level import LogLevel


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
                "-o", "test_outputX",
                "-tl", "academicWeeks", "students",
                "-l", "debug",
                "-de", "True",
            ]

            return parse_main_arguments()

        def it_sets_base_url(main_arguments: MainArguments) -> None:
            assert main_arguments.baseUrl == "http://api.ed-fi.org/v5.1"

        def it_sets_api_key(main_arguments: MainArguments) -> None:
            assert main_arguments.key == "populatedTemplateX"

        def it_sets_api_secret(main_arguments: MainArguments) -> None:
            assert main_arguments.secret == "populatedSecretX"

        def it_sets_ignore_certificate_errors(main_arguments: MainArguments) -> None:
            assert main_arguments.ignoreCertificateErrors is False

        def it_sets_delete_resources(main_arguments: MainArguments) -> None:
            assert main_arguments.deleteResources is False

        def it_sets_resource_list(main_arguments: MainArguments) -> None:
            assert main_arguments.testList == ["academicWeeks", "students"]

        def it_sets_fail_deliberately(main_arguments: MainArguments) -> None:
            assert main_arguments.failDeliberately is False

        def it_sets_output_dir(main_arguments: MainArguments) -> None:
            assert main_arguments.output == "test_outputX"

        def it_sets_log_level(main_arguments: MainArguments) -> None:
            assert main_arguments.log_level == LogLevel.DEBUG

        def it_sets_disableEnrollments(main_arguments: MainArguments) -> None:
            assert main_arguments.disableComposites == "True"


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
        os.environ["PERF_OUTPUT_DIR"] = "test_output"
        os.environ["PERF_LOG_LEVEL"] = "WARNing"
        os.environ["PERF_DESCRIPTION"] = "page run"
        os.environ["IGNORE_TLS_CERTIFICATE"] = "True"
        os.environ["PERF_DELETE_RESOURCES"] = "True"
        os.environ["PERF_TEST_LIST"] = '["a", "b"]'
        os.environ["PERF_FAIL_DELIBERATELY"] = "True"
        os.environ["PERF_DISABLE_COMPOSITES"] = "True"
        sys.argv = ["pytest"]

        return parse_main_arguments()

    def it_sets_base_url(main_arguments: MainArguments) -> None:
        assert main_arguments.baseUrl == "http://api.ed-fi.org"

    def it_sets_api_key(main_arguments: MainArguments) -> None:
        assert main_arguments.key == "populatedTemplate"

    def it_sets_api_secret(main_arguments: MainArguments) -> None:
        assert main_arguments.secret == "populatedSecret"

    def it_sets_ignore_certificate_errors(main_arguments: MainArguments) -> None:
        assert main_arguments.ignoreCertificateErrors is True

    def it_sets_delete_resources(main_arguments: MainArguments) -> None:
        assert main_arguments.deleteResources is True

    def it_sets_resource_list(main_arguments: MainArguments) -> None:
        assert main_arguments.testList == ["a", "b"]

    def it_sets_fail_deliberately(main_arguments: MainArguments) -> None:
        assert main_arguments.failDeliberately is True

    def it_sets_output_dir(main_arguments: MainArguments) -> None:
        assert main_arguments.output == "test_output"

    def it_sets_log_level(main_arguments: MainArguments) -> None:
        assert main_arguments.log_level == LogLevel.WARNING

    def it_sets_disableEnrollments(main_arguments: MainArguments) -> None:
        assert main_arguments.disableComposites == "True"
