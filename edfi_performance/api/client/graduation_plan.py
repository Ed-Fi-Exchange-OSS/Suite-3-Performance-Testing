# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from edfi_performance.api.client import EdFiAPIClient


class GraduationPlanClient(EdFiAPIClient):
    endpoint = 'graduationPlans'

    dependencies = {
        'edfi_performance.api.client.school.SchoolClient': {
            'client_name': 'school_client'
        }
    }

    def create_with_dependencies(self, **kwargs):
        school_reference = self.school_client.create_with_dependencies()

        graduation_plan_attrs = self.factory.build_dict(
            educationOrganizationReference__educationOrganizationId=school_reference['attributes']['schoolId'],
            **kwargs
        )
        graduation_plan_id = self.create(**graduation_plan_attrs)

        return {
            'resource_id': graduation_plan_id,
            'dependency_ids': {
                'school_reference': school_reference,
            },
            'attributes': graduation_plan_attrs,
        }

    def delete_with_dependencies(self, reference, **kwargs):
        self.delete(reference['resource_id'])
        self.school_client.delete_with_dependencies(reference['dependency_ids']['school_reference'])
