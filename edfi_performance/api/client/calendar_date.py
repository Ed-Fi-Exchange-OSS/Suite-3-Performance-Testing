# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from edfi_performance.api.client import EdFiAPIClient
from edfi_performance.api.client.school import SchoolClient
from edfi_performance.factories.utils import RandomSuffixAttribute


class CalendarDateClient(EdFiAPIClient):
    endpoint = 'calendarDates'

    dependencies = {
        'edfi_performance.api.client.calendar.CalendarClient': {},
    }

    def create_with_dependencies(self, **kwargs):
        school_id = kwargs.pop('schoolId', SchoolClient.shared_elementary_school_id())
        custom_calendar_code = kwargs.pop('calendarCode', RandomSuffixAttribute("107SS111111"))
        # Create a calendar
        calendar_reference = self.calendar_client.create_with_dependencies(
            schoolReference__schoolId=school_id,
            calendarCode=custom_calendar_code)

        # Create first calendar date
        calendar_date_attrs = self.factory.build_dict(
            calendarReference__calendarCode=calendar_reference['attributes']['calendarCode'],
            calendarReference__schoolId=school_id,
            calendarReference__schoolYear=2014,
            **kwargs
        )
        calendar_date_id = self.create(**calendar_date_attrs)

        return {
            'resource_id': calendar_date_id,
            'dependency_ids': {
                'calendar_reference': calendar_reference,
            },
            'attributes': calendar_date_attrs,
        }

    def delete_with_dependencies(self, reference, **kwargs):
        self.delete(reference['resource_id'])
        self.calendar_client.delete_with_dependencies(reference['dependency_ids']['calendar_reference'])
