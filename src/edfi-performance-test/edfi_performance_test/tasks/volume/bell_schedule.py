# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from locust import task

from edfi_performance_test.tasks.volume.ed_fi_volume_test_base import EdFiVolumeTestBase
from edfi_performance_test.factories.utils import RandomSuffixAttribute
from edfi_performance_test.api.client.school import SchoolClient

class BellScheduleVolumeTest(EdFiVolumeTestBase):
    @task
    def run_bell_schedule_scenarios(self):
        high_school_id = SchoolClient.shared_high_school_id()
        self.run_scenario("bellScheduleName","Normal Schedule A")
        self.run_scenario(
            "bellScheduleName",
            "Normal Schedule B",
            classPeriodReference__classPeriodName="Class Period 1",
            classPeriodReference__schoolId=high_school_id,
            schoolReference__schoolId=high_school_id,
            alternateDayName="A",
        )
