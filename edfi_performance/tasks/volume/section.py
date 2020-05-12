from locust import task

from edfi_performance.api.client.school import SchoolClient
from edfi_performance.factories.utils import RandomSuffixAttribute
from edfi_performance.tasks.volume import EdFiVolumeTestBase


class SectionVolumeTest(EdFiVolumeTestBase):
    @task
    def run_section_scenarios(self):
        self.run_scenario('availableCredits', 2)
        self.run_scenario('availableCredits', 3,
                          schoolId=SchoolClient.shared_high_school_id(),
                          sectionIdentifier=RandomSuffixAttribute("ALG12017RM901"),
                          courseCode="ALG-2")
