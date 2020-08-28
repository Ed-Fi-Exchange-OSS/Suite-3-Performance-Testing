# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from edfi_performance.api.client import EdFiAPIClient


class PostSecondaryInstitutionClient(EdFiAPIClient):
    endpoint = 'postSecondaryInstitutions'


class PostSecondaryEventClient(EdFiAPIClient):
    endpoint = 'postSecondaryEvents'

    dependencies = {
        PostSecondaryInstitutionClient: {
            'client_name': 'institution_client'
        }
    }

    def create_with_dependencies(self, **kwargs):
        # Create new student for association
        institution_reference = self.institution_client.create_with_dependencies()

        event_attrs = self.factory.build_dict(
            postSecondaryInstitutionReference__postSecondaryInstitutionId=
            institution_reference['attributes']['postSecondaryInstitutionId'],
            **kwargs
        )
        event_id = self.create(**event_attrs)

        return {
            'resource_id': event_id,
            'dependency_ids': {
                'institution_reference': institution_reference,
            },
            'attributes': event_attrs,
        }

    def delete_with_dependencies(self, reference, **kwargs):
        self.delete(reference['resource_id'])
        self.institution_client.delete_with_dependencies(reference['dependency_ids']['institution_reference'])
