# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from locust import task

from edfi_performance.api.client.school import SchoolClient
from edfi_performance.tasks.volume import EdFiVolumeTestBase


class SessionVolumeTest(EdFiVolumeTestBase):
    @task
    def run_session_scenarios(self):
        self.run_scenario('endDate', "2014-12-16")
        self.run_scenario('endDate', "2014-12-16", schoolId=SchoolClient.shared_high_school_id())
