from locust import task

from edfi_performance.api.client.school import SchoolClient
from edfi_performance.factories.utils import RandomSuffixAttribute
from edfi_performance.tasks.volume import EdFiVolumeTestBase


class ClassPeriodVolumeTest(EdFiVolumeTestBase):
    @task
    def run_class_period_scenarios(self):
        self.run_scenario('classPeriodName', RandomSuffixAttribute("Class Period 01", suffix_length=10))
        self.run_scenario('classPeriodName', RandomSuffixAttribute("Class Period 01", suffix_length=10),
                          schoolReference__schoolId=SchoolClient.shared_high_school_id(),
                          meetingTimes=[
                              {
                                  "endTime": "09:25:00",
                                  "startTime": "08:35:00"
                              }
                          ])
