import factory

from edfi_performance.api.client.school import SchoolClient
from edfi_performance.factories.utils import current_year
from .. import APIFactory
from ..descriptors.utils import build_descriptor_dicts


class CalendarDateFactory(APIFactory):
    calendarReference = factory.Dict(
        dict(
            calendarCode="107SS111111",
            schoolId=SchoolClient.shared_elementary_school_id(),
            schoolYear=current_year(),
        )
    )
    calendarEvents = build_descriptor_dicts('CalendarEvent', ['Holiday'])
    date = "2014-09-16"
