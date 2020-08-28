# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from locust import task

from edfi_performance.factories.descriptors.utils import build_descriptor
from edfi_performance.tasks.volume import EdFiVolumeTestBase


class GraduationPlanVolumeTest(EdFiVolumeTestBase):
    @task
    def run_graduation_plan_scenarios(self):
        self.run_scenario('totalRequiredCredits', 30)
        self.run_scenario('totalRequiredCredits', 24,
                          totalRequiredCredits=26,
                          graduationPlanTypeDescriptor=build_descriptor('GraduationPlanType', 'Minimum'))
