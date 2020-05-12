import factory

from edfi_performance.api.client.school import SchoolClient
from edfi_performance.factories import APIFactory
from edfi_performance.factories.utils import UniqueIdAttribute, formatted_date


class AcademicWeekFactory(APIFactory):
    weekIdentifier = UniqueIdAttribute()
    schoolReference = factory.Dict(dict(schoolId=SchoolClient.shared_elementary_school_id()))
    beginDate = formatted_date(8, 7)
    endDate = formatted_date(8, 13)
    totalInstructionalDays = 5
