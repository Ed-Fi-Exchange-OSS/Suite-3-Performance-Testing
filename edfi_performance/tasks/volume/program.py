# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from locust import task

from edfi_performance.tasks.volume import EdFiVolumeTestBase


class ProgramVolumeTest(EdFiVolumeTestBase):
    @task
    def run_program_scenario(self):
        self.run_scenario()
