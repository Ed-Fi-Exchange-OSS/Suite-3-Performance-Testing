# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from locust import task

from edfi_performance_test.api.client.school import SchoolClient
from edfi_performance_test.factories.descriptors.utils import build_descriptor_dicts
from edfi_performance_test.factories.utils import RandomSuffixAttribute
from edfi_performance_test.tasks.volume.ed_fi_volume_test_base import EdFiVolumeTestBase


class CalendarDateVolumeTest(EdFiVolumeTestBase):
    @task
    def run_calendar_scenarios(self):
        self.run_scenario(
            "calendarEvents",
            build_descriptor_dicts(
                "CalendarEvent",
                ["Instructional day", "Student late arrival/early dismissal"],
            ),
        )
        self.run_scenario(
            "calendarEvents",
            build_descriptor_dicts("CalendarEvent", ["Instructional day"]),
            calendarEvents=build_descriptor_dicts("CalendarEvent", ["Holiday"]),
            schoolId=SchoolClient.shared_high_school_id(),
            calendarCode=RandomSuffixAttribute("IEP001"),
        )
