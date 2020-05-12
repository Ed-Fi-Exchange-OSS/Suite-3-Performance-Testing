from locust import task

from edfi_performance.api.client.school import SchoolClient
from edfi_performance.factories.utils import RandomSuffixAttribute
from edfi_performance.tasks.volume import EdFiVolumeTestBase


class LocationVolumeTest(EdFiVolumeTestBase):
    @task
    def run_location_scenarios(self):
        self.run_scenario('maximumNumberOfSeats', 20)
        self.run_scenario('maximumNumberOfSeats', 18,
                          classroomIdentificationCode=RandomSuffixAttribute("901"),
                          schoolReference__schoolId=SchoolClient.shared_high_school_id())
