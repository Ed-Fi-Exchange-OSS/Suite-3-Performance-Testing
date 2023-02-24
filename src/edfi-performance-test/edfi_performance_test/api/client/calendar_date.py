# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from typing import Dict
from edfi_performance_test.api.client.ed_fi_api_client import EdFiAPIClient
from edfi_performance_test.api.client.school import SchoolClient
from edfi_performance_test.factories.utils import RandomSuffixAttribute


class CalendarDateClient(EdFiAPIClient):
    endpoint = "calendarDates"

    dependencies: Dict = {
        "edfi_performance_test.api.client.calendar.CalendarClient": {},
    }

    def create_with_dependencies(self, **kwargs):
        school_id = kwargs.pop("schoolId", SchoolClient.shared_elementary_school_id())
        custom_calendar_code = kwargs.pop(
            "calendarCode", RandomSuffixAttribute("107SS111111")
        )
        # Create a calendar
        calendar_reference = self.calendar_client.create_with_dependencies(  # type: ignore
            schoolReference__schoolId=school_id, calendarCode=custom_calendar_code
        )

        # Create first calendar date
        return self.create_using_dependencies(
            calendar_reference,
            calendarReference__calendarCode=calendar_reference["attributes"][
                "calendarCode"
            ],
            calendarReference__schoolId=school_id,
            calendarReference__schoolYear=calendar_reference["attributes"][
                "schoolYearTypeReference"
            ]["schoolYear"],
            **kwargs
        )
