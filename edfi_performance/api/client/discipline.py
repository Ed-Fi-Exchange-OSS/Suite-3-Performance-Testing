# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from edfi_performance.api.client import EdFiAPIClient
from edfi_performance.api.client.school import SchoolClient
from edfi_performance.api.client.staff import StaffClient
from edfi_performance.api.client.student import StudentClient
from edfi_performance.api.client.student import StudentDisciplineIncidentAssociationClient


class DisciplineIncidentClient(EdFiAPIClient):
    endpoint = 'disciplineIncidents'

    dependencies = {
        StaffClient: {}
    }

    def create_with_dependencies(self, **kwargs):
        school_id = kwargs.pop('schoolId', SchoolClient.shared_elementary_school_id())

        # Create staff
        staff_reference = self.staff_client.create_with_dependencies(schoolId=school_id)

        # Create discipline incident
        incident_attrs = self.factory.build_dict(
            staffReference__staffUniqueId=staff_reference['attributes']['staffUniqueId'],
            schoolReference__schoolId=school_id,
            **kwargs
        )
        incident_id = self.create(**incident_attrs)

        return {
            'resource_id': incident_id,
            'dependency_ids': {
                'staff_reference': staff_reference
            },
            'attributes': incident_attrs,
        }

    def delete_with_dependencies(self, reference, **kwargs):
        self.delete(reference['resource_id'])
        self.staff_client.delete_with_dependencies(reference['dependency_ids']['staff_reference'])


class DisciplineActionClient(EdFiAPIClient):
    endpoint = 'disciplineActions'

    dependencies = {
        StudentDisciplineIncidentAssociationClient: {
            'client_name': 'assoc_client',
        }
    }

    def create_with_dependencies(self, **kwargs):
        # Create incident and association first
        school_id = kwargs.pop('schoolId', SchoolClient.shared_elementary_school_id())

        assoc_reference = self.assoc_client.create_with_dependencies(schoolId=school_id)

        # Create discipline action
        action_attrs = self.factory.build_dict(
            studentReference__studentUniqueId=assoc_reference['attributes']['studentReference']['studentUniqueId'],
            studentDisciplineIncidentAssociations__0__studentDisciplineIncidentAssociationReference__incidentIdentifier
            =assoc_reference['attributes']['disciplineIncidentReference']['incidentIdentifier'],
            studentDisciplineIncidentAssociations__0__studentDisciplineIncidentAssociationReference__studentUniqueId
            =assoc_reference['attributes']['studentReference']['studentUniqueId'],
            studentDisciplineIncidentAssociations__0__studentDisciplineIncidentAssociationReference__schoolId=school_id,
            **kwargs
        )
        action_id = self.create(**action_attrs)

        return {
            'resource_id': action_id,
            'dependency_ids': {
                'assoc_reference': assoc_reference
            },
            'attributes': action_attrs,
        }

    def delete_with_dependencies(self, reference, **kwargs):
        self.delete(reference['resource_id'])
        self.assoc_client.delete_with_dependencies(reference['dependency_ids']['assoc_reference'])
