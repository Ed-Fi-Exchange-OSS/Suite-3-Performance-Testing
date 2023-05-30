# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from datetime import date

from edfi_performance_test.factories.utils import formatted_date


def describe_when_formatting_a_date() -> None:
    def describe_given_no_year_provided() -> None:
        def it_formats_using_current_year() -> None:
            month = 12
            day = 1
            expected = str(date.today().year) + "-12-01"

            actual = formatted_date(month, day)

            assert actual == expected

    def describe_given_year_is_provided() -> None:
        def it_formats_using_the_given_year() -> None:
            year = 1999
            month = 12
            day = 1
            expected = "1999-12-01"

            actual = formatted_date(month, day, year)

            assert actual == expected
