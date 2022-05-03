# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from edfi_paging_test.helpers.log_level import LogLevel
from edfi_paging_test.helpers.output_format import OutputFormat
import pytest
from edfi_paging_test.reporter.summary import Summary
from edfi_paging_test.helpers.main_arguments import MainArguments
import socket


def describe_when_initializing_summary() -> None:
    DEFAULT_RESOURCE_LIST = ["all"]

    def describe_when_all_fields_are_provided() -> None:
        @pytest.fixture()
        def summary() -> Summary:
            return Summary(
                run_name="123",
                machine_name="m1",
                run_configration=MainArguments(
                    "http://api.ed-fi.org/v5.1",
                    4,
                    "populatedTemplateX",
                    "populatedSecretX",
                    True,
                    "test_outputX",
                    "test",
                    OutputFormat.CSV,
                    ["resource1", "resource2"],
                    100,
                    LogLevel.DEBUG,
                )
            )

        def it_sets_run_name(summary: Summary) -> None:
            assert summary.run_name == "123"

        def it_sets_description(summary: Summary) -> None:
            assert summary.run_configration.description == "test"

        def it_sets_machine_name(summary: Summary) -> None:
            assert summary.machine_name == "m1"

        def it_sets_resources(summary: Summary) -> None:
            assert summary.run_configration.resourceList == ["resource1", "resource2"]

    def describe_when_resource_not_provided() -> None:
        @pytest.fixture()
        def summary_without_resources() -> Summary:
            return Summary(
                run_name="123",
                run_configration=MainArguments(
                    "http://api.ed-fi.org/v5.1",
                    4,
                    "populatedTemplateX",
                    "populatedSecretX",
                    True,
                    "test_outputX",
                    "test",
                    OutputFormat.CSV,
                    [],
                    100,
                    LogLevel.DEBUG,
                )
            )

        def it_sets_default_value_for_resources(summary_without_resources: Summary) -> None:
            assert summary_without_resources.run_configration.resourceList == DEFAULT_RESOURCE_LIST

    def describe_when_machine_name_not_provided() -> None:
        @pytest.fixture()
        def summary_without_host() -> Summary:
            return Summary(
                run_name="123",
                run_configration=MainArguments(
                    "http://api.ed-fi.org/v5.1",
                    4,
                    "populatedTemplateX",
                    "populatedSecretX",
                    True,
                    "test_outputX",
                    "test",
                    OutputFormat.CSV,
                    ["resource1", "resource2"],
                    100,
                    LogLevel.DEBUG,
                )
            )

        def it_sets_system_name(summary_without_host: Summary) -> None:
            assert summary_without_host.machine_name == socket.gethostname()
