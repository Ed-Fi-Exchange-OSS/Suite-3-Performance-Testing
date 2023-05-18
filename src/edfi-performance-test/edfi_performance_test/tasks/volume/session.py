# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from locust import task

from edfi_performance_test.tasks.volume.ed_fi_volume_test_base import EdFiVolumeTestBase
from edfi_performance_test.factories.utils import RandomSuffixAttribute
from edfi_performance_test.api.client.school import SchoolClient
from edfi_performance_test.factories.descriptors.utils import build_descriptor
import factory

class SessionVolumeTest(EdFiVolumeTestBase):
    @task
    def ru_session_scenarios(self):
        self.run_scenario("sessionName",RandomSuffixAttribute("Fall Semester", suffix_length=4))
        self.run_scenario(
            "sessionName",
            RandomSuffixAttribute("Fall Semester", suffix_length=4),
            schoolReference__schoolId=SchoolClient.shared_high_school_id(),
            SchoolYearTypeReference__schoolYear=2023,
            beginDate="2023-10-06",
            endDate="2023-12-15",
            termDescriptor=build_descriptor("Term", "Fall Semester"),
            totalInstructionalDays=30,
            gradingPeriodReference__gradingPeriodDescriptor= factory.Dict(
                dict(
                    gradingPeriodDescriptor=build_descriptor(
                        "GradingPeriod", "First Six Weeks"
                    ),
                        periodSequence=None,  # Must be entered by user
                        schoolId=SchoolClient.shared_elementary_school_id(),
                        schoolYear=2014,
                    )
                ),
        )
