import factory

from edfi_performance.api.client.school import SchoolClient
from edfi_performance.factories import APIFactory
from edfi_performance.factories.descriptors.utils import build_descriptor
from edfi_performance.factories.utils import formatted_date, UniqueIdAttribute


class DisciplineActionFactory(APIFactory):
    disciplineActionIdentifier = UniqueIdAttribute(num_chars=20)
    disciplineDate = formatted_date(9, 20)
    disciplines = factory.List([
        factory.Dict(dict(disciplineDescriptor=build_descriptor('Discipline', 'Out of School Suspension'))),
    ])
    studentReference = factory.Dict(dict(studentUniqueId=111111))  # Default value for scenarios, but not in DB
    actualDisciplineActionLength = 2
    studentDisciplineIncidentAssociations = factory.List([
        factory.Dict(
            dict(
                studentDisciplineIncidentAssociationReference=factory.Dict(dict(
                    incidentIdentifier=None,  # Must be entered by user
                    schoolId=SchoolClient.shared_elementary_school_id(),  # Prepopulated school
                    studentUniqueId=111111,  # Default value for scenarios, but not in DB
                )),
            ),
        ),
    ])
    responsibilitySchoolReference = factory.Dict(dict(schoolId=SchoolClient.shared_elementary_school_id()))  # Prepopulated school


class DisciplineIncidentFactory(APIFactory):
    incidentDate = formatted_date(9, 25)
    incidentIdentifier = UniqueIdAttribute(num_chars=20)
    schoolReference = factory.Dict(dict(schoolId=SchoolClient.shared_elementary_school_id()))  # Prepopulated school
    staffReference = factory.Dict(dict(staffUniqueId=None))  # Must be entered by user
    behaviors = factory.List([
        factory.Dict(
            dict(behaviorDescriptor=build_descriptor('Behavior', 'School Code of Conduct')),
        )
    ])
    incidentLocationDescriptor = build_descriptor('IncidentLocation', 'School Bus')
    reporterDescriptionDescriptor = build_descriptor('ReporterDescription', 'Staff')
    reporterName = "Villa, Mike"
