# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from typing import Dict
from edfi_performance_test.api.client.ed_fi_api_client import EdFiAPIClient
from edfi_performance_test.api.client.school import SchoolClient
from edfi_performance_test.api.client.student import (
    StudentClient,
)


class DisciplineActionClientV5(EdFiAPIClient):
    endpoint = "disciplineActions"

    dependencies: Dict = {StudentClient: {}}

    def create_with_dependencies(self, **kwargs):
        # Create incident and association first
        school_id = kwargs.pop("schoolId", SchoolClient.shared_elementary_school_id())

        student_reference = self.student_client.create_with_dependencies(schoolId=school_id)

        # Create discipline action
        return self.create_using_dependencies(
            student_reference,
            studentReference__studentUniqueId=student_reference["attributes"]["studentUniqueId"],
            **kwargs
        )
