# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import pytest

from edfi_paging_test.helpers.output_format import OutputFormat


def describe_when_parsing_enum() -> None:
    def describe_given_valid_options_with_mixed_cases() -> None:
        @pytest.mark.parametrize("input, expected", [
            ("jSoN", OutputFormat.JSON),
            ("JSON", OutputFormat.JSON),
            ("json", OutputFormat.JSON),
            ("CsV", OutputFormat.CSV),
            ("CSV", OutputFormat.CSV),
            ("csv", OutputFormat.CSV),
        ])
        def it_translates_correctly(input: str, expected: OutputFormat) -> None:
            assert OutputFormat(input) == expected

    def describe_given_invalid_option() -> None:
        @pytest.mark.parametrize("input", ["csv_", "jsonp", "txt"])
        def it_raises_ValueError(input: str) -> None:
            with pytest.raises(ValueError):
                OutputFormat(input)
