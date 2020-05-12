from locust import task

from edfi_performance.api.client.school import SchoolClient
from edfi_performance.factories.descriptors.utils import build_descriptor
from edfi_performance.tasks.volume import EdFiVolumeTestBase


class GradingPeriodVolumeTest(EdFiVolumeTestBase):
    @task
    def run_grading_period_scenarios(self):
        high_school_id = SchoolClient.shared_high_school_id()
        self.run_scenario('endDate', "2014-10-05")
        self.run_scenario(beginDate="2014-10-06",
                          endDate="2014-12-15",
                          totalInstructionalDays=30,
                          gradingPeriodDescriptor=build_descriptor("GradingPeriod", "Second Six Weeks"))
        self.run_scenario('endDate', "2014-10-05",
                          schoolReference__schoolId=high_school_id)
        self.run_scenario(schoolReference__schoolId=high_school_id,
                          beginDate="2014-10-06",
                          endDate="2014-12-15",
                          totalInstructionalDays=30,
                          gradingPeriodDescriptor=build_descriptor("GradingPeriod", "Second Six Weeks"))
