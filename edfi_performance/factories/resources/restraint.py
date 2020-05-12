import factory

from edfi_performance.api.client.school import SchoolClient
from edfi_performance.api.client.student import StudentClient
from edfi_performance.factories import APIFactory
from edfi_performance.factories.utils import UniqueIdAttribute, formatted_date


class RestraintEventFactory(APIFactory):
    restraintEventIdentifier = UniqueIdAttribute(num_chars=20)
    schoolReference = factory.Dict(dict(schoolId=SchoolClient.shared_elementary_school_id()))
    studentReference = factory.Dict(dict(studentUniqueId=StudentClient.shared_student_id()))
    eventDate = formatted_date(2, 14)
