# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from edfi_performance_test.api.client.ed_fi_api_client import EdFiAPIClient


class GraduationPlanClient(EdFiAPIClient):
    endpoint = "graduationPlans"

    dependencies = {
        "edfi_performance_test.api.client.school.SchoolClient": {
            "client_name": "school_client"
        }
    }

    def create_with_dependencies(self, **kwargs):
        school_reference = self.school_client.create_with_dependencies()  # type: ignore

        return self.create_using_dependencies(
            school_reference,
            educationOrganizationReference__educationOrganizationId=school_reference[
                "attributes"
            ]["schoolId"],
            **kwargs
        )
