from edfi_performance.api.client import EdFiAPIClient
from edfi_performance.api.client.school import SchoolClient
from edfi_performance.api.client.staff import StaffClient
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
        return self.create_using_dependencies(
            staff_reference,
            staffReference__staffUniqueId=staff_reference['attributes']['staffUniqueId'],
            schoolReference__schoolId=school_id,
            **kwargs
        )


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
        return self.create_using_dependencies(
            assoc_reference,
            studentReference__studentUniqueId=assoc_reference['attributes']['studentReference']['studentUniqueId'],
            studentDisciplineIncidentAssociations__0__studentDisciplineIncidentAssociationReference__incidentIdentifier
            =assoc_reference['attributes']['disciplineIncidentReference']['incidentIdentifier'],
            studentDisciplineIncidentAssociations__0__studentDisciplineIncidentAssociationReference__studentUniqueId
            =assoc_reference['attributes']['studentReference']['studentUniqueId'],
            studentDisciplineIncidentAssociations__0__studentDisciplineIncidentAssociationReference__schoolId=school_id,
            **kwargs
        )
