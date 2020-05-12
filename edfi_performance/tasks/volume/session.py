from locust import task

from edfi_performance.api.client.school import SchoolClient
from edfi_performance.tasks.volume import EdFiVolumeTestBase


class SessionVolumeTest(EdFiVolumeTestBase):
    @task
    def run_session_scenarios(self):
        self.run_scenario('endDate', "2014-12-16")
        self.run_scenario('endDate', "2014-12-16", schoolId=SchoolClient.shared_high_school_id())
