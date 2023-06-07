# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from locust import task

from edfi_performance_test.tasks.volume.ed_fi_volume_test_base import EdFiVolumeTestBase
from edfi_performance_test.factories.resources.api_factory import APIFactory
import logging


logger = logging.getLogger()


class ChartOfAccountVolumeTest(EdFiVolumeTestBase):
    @task
    def run_grade_scenarios(self):
        if APIFactory.version.startswith("4"):
            logger.info("entra ChartOfAccountVolumeTest")
            self.run_scenario("accountName", "Test Char of Account II")
