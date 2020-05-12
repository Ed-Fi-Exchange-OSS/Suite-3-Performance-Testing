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
