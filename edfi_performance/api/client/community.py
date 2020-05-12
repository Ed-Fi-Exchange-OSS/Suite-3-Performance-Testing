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

        return self.create_using_dependencies(
            org_reference,
            communityOrganizationReference__communityOrganizationId=org_reference['attributes']['communityOrganizationId'],
            **kwargs
        )


class CommunityProviderLicenseClient(EdFiAPIClient):
    endpoint = 'communityProviderLicenses'

    dependencies = {
        CommunityProviderClient: {
            'client_name': 'provider_client',
        },
    }

    def create_with_dependencies(self, **kwargs):
        provider_reference = self.provider_client.create_with_dependencies()

        return self.create_using_dependencies(
            provider_reference,
            communityProviderReference__communityProviderId=provider_reference['attributes']['communityProviderId'],
            **kwargs
        )
