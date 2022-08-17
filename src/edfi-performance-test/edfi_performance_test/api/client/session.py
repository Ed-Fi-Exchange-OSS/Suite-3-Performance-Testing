# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from typing import Dict
from edfi_performance_test.api.client.ed_fi_api_client import EdFiAPIClient
from edfi_performance_test.api.client.grading_period import GradingPeriodClient
from edfi_performance_test.api.client.school import SchoolClient
from edfi_performance_test.factories.descriptors.utils import build_descriptor


class SessionClient(EdFiAPIClient):
    endpoint = "sessions"

    dependencies: Dict = {GradingPeriodClient: {}}

    def create_with_dependencies(self, **kwargs):
        school_id = kwargs.pop("schoolId", SchoolClient.shared_elementary_school_id())
        school_year = kwargs.get("schoolYear", 2014)
        # Create two grading periods
        period_1_reference = self.grading_period_client.create_with_dependencies(
            schoolReference__schoolId=school_id,
            schoolYearTypeReference__schoolYear=school_year,
        )
        period_2_reference = self.grading_period_client.create_with_dependencies(
            schoolReference__schoolId=school_id,
            schoolYearTypeReference__schoolYear=school_year,
            beginDate="2014-10-06",
            endDate="2014-12-15",
            totalInstructionalDays=30,
            gradingPeriodDescriptor=build_descriptor(
                "GradingPeriod", "Second Six Weeks"
            ),
        )

        # Create session referencing grading periods
        return self.create_using_dependencies(
            [
                {"period_1_reference": period_1_reference},
                {"period_2_reference": period_2_reference},
            ],
            schoolReference__schoolId=school_id,
            schoolYearTypeReference__schoolYear=school_year,
            gradingPeriods__0__gradingPeriodReference__periodSequence=period_1_reference[
                "attributes"
            ][
                "periodSequence"
            ],
            gradingPeriods__1__gradingPeriodReference__periodSequence=period_2_reference[
                "attributes"
            ][
                "periodSequence"
            ],
            **kwargs
        )

    def delete_with_dependencies(self, reference, **kwargs):
        self.delete_item(reference["resource_id"])
        self.grading_period_client.delete_with_dependencies(
            reference["dependency_ids"]["period_1_reference"]
        )
        self.grading_period_client.delete_with_dependencies(
            reference["dependency_ids"]["period_2_reference"]
        )
