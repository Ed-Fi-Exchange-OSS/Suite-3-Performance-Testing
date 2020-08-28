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

        return self.create_using_dependencies(
            institution_reference,
            postSecondaryInstitutionReference__postSecondaryInstitutionId=
            institution_reference['attributes']['postSecondaryInstitutionId'],
            **kwargs
        )
