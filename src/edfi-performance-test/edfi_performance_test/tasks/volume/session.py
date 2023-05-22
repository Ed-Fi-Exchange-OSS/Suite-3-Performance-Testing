# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from locust import task

from edfi_performance_test.tasks.volume.ed_fi_volume_test_base import EdFiVolumeTestBase
from edfi_performance_test.factories.utils import RandomSuffixAttribute
from edfi_performance_test.api.client.school import SchoolClient
from edfi_performance_test.factories.descriptors.utils import build_descriptor
from edfi_performance_test.factories.utils import formatted_date

class SessionVolumeTest(EdFiVolumeTestBase):
    @task
    def ru_session_scenarios(self):
        self.run_scenario("sessionName","Fall Semester")
        self.run_scenario(
            "endDate",
            formatted_date(12, 10),
            totalInstructionalDays=30,
        )
