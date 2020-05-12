from edfi_performance.api.client import EdFiAPIClient
from edfi_performance.api.client.school import SchoolClient
from edfi_performance.factories.utils import RandomSuffixAttribute


class CalendarDateClient(EdFiAPIClient):
    endpoint = 'calendarDates'

    dependencies = {
        'edfi_performance.api.client.calendar.CalendarClient': {},
    }

    def create_with_dependencies(self, **kwargs):
        school_id = kwargs.pop('schoolId', SchoolClient.shared_elementary_school_id())
        custom_calendar_code = kwargs.pop('calendarCode', RandomSuffixAttribute("107SS111111"))
        # Create a calendar
        calendar_reference = self.calendar_client.create_with_dependencies(
            schoolReference__schoolId=school_id,
            calendarCode=custom_calendar_code)

        # Create first calendar date
        return self.create_using_dependencies(
            calendar_reference,
            calendarReference__calendarCode=calendar_reference['attributes']['calendarCode'],
            calendarReference__schoolId=school_id,
            calendarReference__schoolYear=2014,
            **kwargs)
