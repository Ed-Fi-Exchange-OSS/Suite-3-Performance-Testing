# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from typing import Dict
from edfi_performance_test.api.client.ed_fi_api_client import EdFiAPIClient
from edfi_performance_test.api.client.school import SchoolClient


class CourseOfferingClient(EdFiAPIClient):
    endpoint = "courseOfferings"

    dependencies: Dict = {"edfi_performance_test.api.client.session.SessionClient": {}}

    def create_with_dependencies(self, **kwargs):
        school_id = kwargs.pop("schoolId", SchoolClient.shared_elementary_school_id())
        school_year = kwargs.get("schoolYear", 2014)
        course_code = kwargs.pop("courseCode", "ELA-01")
        session_reference = self.session_client.create_with_dependencies(
            schoolId=school_id, schoolYear=school_year
        )

        return self.create_using_dependencies(
            session_reference,
            sessionReference__schoolId=school_id,
            sessionReference__schoolYear=school_year,
            sessionReference__sessionName=session_reference["attributes"][
                "sessionName"
            ],
            courseReference_courseCode=course_code,
            courseReference_educationOrganizationId=school_id,
            **kwargs
        )
