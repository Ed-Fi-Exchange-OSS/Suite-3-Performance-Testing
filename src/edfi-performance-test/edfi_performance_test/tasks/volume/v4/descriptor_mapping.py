# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from locust import task

from edfi_performance_test.tasks.volume.ed_fi_volume_test_base import EdFiVolumeTestBase


class DescriptorMappingVolumeTest(EdFiVolumeTestBase):
    @task
    def run_descriptor_mapping_scenarios(self):
        self.run_scenario("Value", "Life and Physical Sciences")
