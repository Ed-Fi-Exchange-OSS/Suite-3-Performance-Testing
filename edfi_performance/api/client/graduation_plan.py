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

        return self.create_using_dependencies(
            school_reference,
            educationOrganizationReference__educationOrganizationId=school_reference['attributes']['schoolId'],
            **kwargs
        )
