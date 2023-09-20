# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from locust import task

from edfi_performance_test.tasks.volume.discipline import (
    DisciplineActionVolumeTest,
)
from edfi_performance_test.api.client.school import SchoolClient
from edfi_performance_test.factories.descriptors.utils import build_descriptor
from edfi_performance_test.tasks.volume.ed_fi_volume_test_base import EdFiVolumeTestBase


class SkipDisciplineActionVolumeTest(DisciplineActionVolumeTest):
    @classmethod
    def skip_all_scenarios(cls):
        return True


class DisciplineActionVolumeTestV5(EdFiVolumeTestBase):
    @task
    def run_discipline_action_scenarios(self):
        self.run_scenario(
            "disciplines",
            [
                {
                    "disciplineDescriptor": build_descriptor(
                        "Discipline", "In School Suspension"
                    )
                }
            ],
        )
        self.run_scenario(
            "disciplines",
            [
                {
                    "disciplineDescriptor": build_descriptor(
                        "Discipline", "Community Service"
                    )
                }
            ],
            schoolId=SchoolClient.shared_high_school_id(),
            disciplines__0__disciplineDescriptor=build_descriptor(
                "Discipline", "In School Suspension"
            ),
            actualDisciplineActionLength=5,
        )
