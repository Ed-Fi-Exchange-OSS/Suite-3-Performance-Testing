# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from edfi_performance_test.api.client.ed_fi_api_client import EdFiAPIClient


class CommunityOrganizationClient(EdFiAPIClient):
    endpoint = "communityOrganizations"


class CommunityProviderClient(EdFiAPIClient):
    endpoint = "communityProviders"

    dependencies = {
        CommunityOrganizationClient: {
            "client_name": "org_client",
        },
    }

    def create_with_dependencies(self, **kwargs):
        org_reference = self.org_client.create_with_dependencies()
        if(org_reference is None or org_reference["resource_id"] is None):
            return

        return self.create_using_dependencies(
            org_reference,
            communityOrganizationReference__communityOrganizationId=org_reference[
                "attributes"
            ]["communityOrganizationId"],
            **kwargs
        )


class CommunityProviderLicenseClient(EdFiAPIClient):
    endpoint = "communityProviderLicenses"

    dependencies = {
        CommunityProviderClient: {
            "client_name": "provider_client",
        },
    }

    def create_with_dependencies(self, **kwargs):
        provider_reference = self.provider_client.create_with_dependencies()
        if(provider_reference is None or provider_reference["resource_id"] is None):
            return

        return self.create_using_dependencies(
            provider_reference,
            communityProviderReference__communityProviderId=provider_reference[
                "attributes"
            ]["communityProviderId"],
            **kwargs
        )
