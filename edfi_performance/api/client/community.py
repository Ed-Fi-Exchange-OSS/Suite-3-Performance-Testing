# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from edfi_performance.api.client import EdFiAPIClient


class CommunityOrganizationClient(EdFiAPIClient):
    endpoint = 'communityOrganizations'


class CommunityProviderClient(EdFiAPIClient):
    endpoint = 'communityProviders'

    dependencies = {
        CommunityOrganizationClient: {
            'client_name': 'org_client',
        },
    }

    def create_with_dependencies(self, **kwargs):
        org_reference = self.org_client.create_with_dependencies()

        provider_attrs = self.factory.build_dict(
            communityOrganizationReference__communityOrganizationId=org_reference['attributes']['communityOrganizationId'],
            **kwargs
        )
        provider_id = self.create(**provider_attrs)

        return {
            'resource_id': provider_id,
            'dependency_ids': {
                'org_reference': org_reference,
            },
            'attributes': provider_attrs,
        }

    def delete_with_dependencies(self, reference, **kwargs):
        self.delete(reference['resource_id'])
        self.org_client.delete_with_dependencies(reference['dependency_ids']['org_reference'])


class CommunityProviderLicenseClient(EdFiAPIClient):
    endpoint = 'communityProviderLicenses'

    dependencies = {
        CommunityProviderClient: {
            'client_name': 'provider_client',
        },
    }

    def create_with_dependencies(self, **kwargs):
        provider_reference = self.provider_client.create_with_dependencies()

        license_attrs = self.factory.build_dict(
            communityProviderReference__communityProviderId=provider_reference['attributes']['communityProviderId'],
            **kwargs
        )
        license_id = self.create(**license_attrs)

        return {
            'resource_id': license_id,
            'dependency_ids': {
                'provider_reference': provider_reference,
            },
            'attributes': license_attrs,
        }

    def delete_with_dependencies(self, reference, **kwargs):
        self.delete(reference['resource_id'])
        self.provider_client.delete_with_dependencies(reference['dependency_ids']['provider_reference'])
