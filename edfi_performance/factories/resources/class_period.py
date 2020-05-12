import factory

from edfi_performance.api.client.school import SchoolClient
from .. import APIFactory
from ..utils import RandomSuffixAttribute


class ClassPeriodFactory(APIFactory):
    classPeriodName = RandomSuffixAttribute("Class Period 1", suffix_length=10)
    schoolReference = factory.Dict(dict(schoolId=SchoolClient.shared_elementary_school_id()))  # Prepopulated school
    officialAttendancePeriod = False
