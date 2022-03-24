# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import pytest
from edfi_paging_test.reporter.summary import Summary
import socket


def describe_when_initializing_summary() -> None:
    DEFAULT_RESOURCE_LIST = ["all"]

    def describe_when_all_fields_are_provided() -> None:
        @pytest.fixture()
        def summary() -> Summary:
            return Summary(
                key="123",
                description="test",
                resources=["resource1", "resource2"],
                machine_name="m1"
            )

        def it_sets_key(summary: Summary) -> None:
            assert summary.key == "123"

        def it_sets_description(summary: Summary) -> None:
            assert summary.description == "test"

        def it_sets_machine_name(summary: Summary) -> None:
            assert summary.machine_name == "m1"

        def it_sets_resources(summary: Summary) -> None:
            assert summary.resources == ["resource1", "resource2"]

    def describe_when_resource_not_provided() -> None:
        @pytest.fixture()
        def summary_without_resources() -> Summary:
            return Summary(
                key="123",
                description="test",
            )

        def it_sets_default_value_for_resources(summary_without_resources: Summary) -> None:
            assert summary_without_resources.resources == DEFAULT_RESOURCE_LIST

    def describe_when_resource_is_None() -> None:
        @pytest.fixture()
        def summary_with_null_resources() -> Summary:
            return Summary(
                key="123",
                description="test",
                resources=[]
            )

        def it_sets_default_value_for_resources(summary_with_null_resources: Summary) -> None:
            assert summary_with_null_resources.resources == DEFAULT_RESOURCE_LIST

    def describe_when_machine_name_not_provided() -> None:
        @pytest.fixture()
        def summary_without_host() -> Summary:
            return Summary(
                key="123",
                description="test",
            )

        def it_sets_system_name(summary_without_host: Summary) -> None:
            assert summary_without_host.machine_name == socket.gethostname()
