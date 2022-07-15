# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from locust import task

from edfi_performance_test.api.client.school import SchoolClient
from edfi_performance_test.factories.utils import RandomSuffixAttribute
from edfi_performance_test.tasks.volume.ed_fi_volume_test_base import EdFiVolumeTestBase


class ClassPeriodVolumeTest(EdFiVolumeTestBase):
    @task
    def run_class_period_scenarios(self):
        self.run_scenario(
            "classPeriodName",
            RandomSuffixAttribute("Class Period 01", suffix_length=10),
        )
        self.run_scenario(
            "classPeriodName",
            RandomSuffixAttribute("Class Period 01", suffix_length=10),
            schoolReference__schoolId=SchoolClient.shared_high_school_id(),
            meetingTimes=[{"endTime": "09:25:00", "startTime": "08:35:00"}],
        )
