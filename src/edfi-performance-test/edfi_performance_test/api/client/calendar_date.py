# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from typing import Dict
from edfi_performance_test.api.client.ed_fi_api_client import EdFiAPIClient
from edfi_performance_test.api.client.school import SchoolClient


class CalendarDateClient(EdFiAPIClient):
    endpoint = "calendarDates"

    dependencies: Dict = {
        "edfi_performance_test.api.client.calendar.CalendarClient": {},
    }

    def create_with_dependencies(self, **kwargs):
        school_id = kwargs.pop("schoolId", SchoolClient.shared_elementary_school_id())
        # Create a calendar
        calendar_reference = self.calendar_client.create_with_dependencies(
            schoolReference__schoolId=school_id
        )
        if(calendar_reference is None or calendar_reference["resource_id"] is None):
            return

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
