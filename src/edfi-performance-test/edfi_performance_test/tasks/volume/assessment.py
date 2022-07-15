# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from locust import task
from edfi_performance_test.tasks.volume.ed_fi_volume_test_base import EdFiVolumeTestBase


class AssessmentVolumeTest(EdFiVolumeTestBase):
    @task
    def run_assessment_scenario(self):
        self.run_scenario("title", "AP English 2")


class AssessmentItemVolumeTest(EdFiVolumeTestBase):
    @task
    def run_assessment_scenario(self):
        self.run_scenario("correctResponse", "B")


class LearningObjectiveVolumeTest(EdFiVolumeTestBase):
    @task
    def run_objective_scenario(self):
        self.run_scenario(
            "description",
            "The student will demonstrate the ability to utilize numbers to perform "
            "operations with complex concepts at a high level.",
        )


class LearningStandardVolumeTest(EdFiVolumeTestBase):
    @task
    def run_learning_standard_scenario(self):
        self.run_scenario("courseTitle", "Advanced Math for students v4.5")


class ObjectiveAssessmentVolumeTest(EdFiVolumeTestBase):
    @task
    def run_assessment_scenario(self):
        self.run_scenario("maxRawScore", 9)


class StudentAssessmentVolumeTest(EdFiVolumeTestBase):
    @task
    def run_assessment_scenario(self):
        self.run_scenario("serialNumber", "1")
