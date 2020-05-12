from locust import task

from edfi_performance.api.client.school import SchoolClient
from edfi_performance.factories.descriptors.utils import build_descriptor
from edfi_performance.factories.utils import RandomSuffixAttribute
from edfi_performance.tasks.volume import EdFiVolumeTestBase


class CohortVolumeTest(EdFiVolumeTestBase):
    @task
    def run_cohort_scenarios(self):
        self.run_scenario('cohortTypeDescriptor', build_descriptor("CohortType", "Field Trip"))
        self.run_scenario('cohortTypeDescriptor', build_descriptor("CohortType", "Extracurricular Activity"),
                          cohortIdentifier=RandomSuffixAttribute("2"),
                          educationOrganizationReference__educationOrganizationId=SchoolClient.shared_high_school_id(),
                          cohortDescription="Cohort 2 Description")
