import factory

from edfi_performance.api.client.school import SchoolClient
from .. import APIFactory
from ..utils import RandomSuffixAttribute


class LocationFactory(APIFactory):
    classroomIdentificationCode = RandomSuffixAttribute("501")
    schoolReference = factory.Dict(dict(schoolId=SchoolClient.shared_elementary_school_id()))  # Prepopulated school
    maximumNumberOfSeats = 22
