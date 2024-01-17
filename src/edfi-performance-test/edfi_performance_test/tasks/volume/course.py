# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from locust import task

from edfi_performance_test.api.client.school import SchoolClient
from edfi_performance_test.factories.descriptors.utils import build_descriptor
from edfi_performance_test.factories.utils import RandomSuffixAttribute
from edfi_performance_test.tasks.volume.ed_fi_volume_test_base import EdFiVolumeTestBase


class CourseVolumeTest(EdFiVolumeTestBase):
    @task
    def run_course_scenarios(self):
        self.run_scenario("courseTitle", "Algebra II")
        self.run_scenario(
            "levelCharacteristics",
            [
                {
                    "courseLevelCharacteristicDescriptor": build_descriptor(
                        "courseLevelCharacteristic", "Basic"
                    )
                }
            ],
            academicSubjectDescriptor=build_descriptor(
                "AcademicSubject", "Fine and Performing Arts"
            ),
            courseTitle="Art, Grade 1",
            courseCode=RandomSuffixAttribute("ART 01"),
        )


class CourseTranscriptVolumeTest(EdFiVolumeTestBase):
    @task
    def run_transcript_scenarios(self):
        self.run_scenario("finalNumericGradeEarned", 87)
        self.run_scenario(
            "finalNumericGradeEarned",
            100,
            schoolId=SchoolClient.shared_high_school_id(),
            courseReference__courseCode="ALG-2",
            finalLetterGradeEarned="A",
            finalNumericGradeEarned=98,
        )
