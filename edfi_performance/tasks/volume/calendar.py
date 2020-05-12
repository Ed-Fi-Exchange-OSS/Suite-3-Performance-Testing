from locust import task

from edfi_performance.api.client.school import SchoolClient
from edfi_performance.factories.descriptors.utils import build_descriptor
from edfi_performance.factories.descriptors.utils import build_descriptor_dicts
from edfi_performance.factories.utils import RandomSuffixAttribute
from edfi_performance.tasks.volume import EdFiVolumeTestBase


class CalendarVolumeTest(EdFiVolumeTestBase):
    @task(weight=100)
    def run_calendar_scenarios(self):
        self.run_scenario('calendarTypeDescriptor', build_descriptor('CalendarType', 'Student Specific'))
        self.run_scenario('gradeLevels', build_descriptor_dicts('GradeLevel', ['Ninth grade', 'Tenth grade']),
                          calendarCode=RandomSuffixAttribute("IEP001"),
                          schoolReference__schoolId=SchoolClient.shared_high_school_id(),
                          gradeLevels=build_descriptor_dicts('GradeLevel', ['Ninth grade']))

    @task(weight=1)
    def deliberate_failure_scenario(self):
        self.run_unsuccessful_scenario(schoolReference__schoolId='INVALID SCHOOL ID',
                                       succeed_on=[403])
