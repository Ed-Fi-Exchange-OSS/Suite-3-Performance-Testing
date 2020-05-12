from locust import task

from edfi_performance.api.client.school import SchoolClient
from edfi_performance.factories.descriptors.utils import build_descriptor_dicts
from edfi_performance.factories.utils import RandomSuffixAttribute
from edfi_performance.tasks.volume import EdFiVolumeTestBase


class CalendarDateVolumeTest(EdFiVolumeTestBase):
    @task
    def run_calendar_scenarios(self):
        self.run_scenario('calendarEvents', build_descriptor_dicts(
            'CalendarEvent', ['Instructional day', 'Student late arrival/early dismissal']))
        self.run_scenario('calendarEvents', build_descriptor_dicts('CalendarEvent', ['Instructional day']),
                          calendarEvents=build_descriptor_dicts('CalendarEvent', ['Holiday']),
                          schoolId=SchoolClient.shared_high_school_id(),
                          calendarCode=RandomSuffixAttribute("IEP001"))
