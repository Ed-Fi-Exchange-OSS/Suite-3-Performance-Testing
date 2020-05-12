from locust import task

from edfi_performance.api.client.school import SchoolClient
from edfi_performance.tasks.volume import EdFiVolumeTestBase


class GradeVolumeTest(EdFiVolumeTestBase):
    @task
    def run_grade_scenarios(self):
        self.run_scenario('numericGradeEarned', 83)
        self.run_scenario('numericGradeEarned', 97,
                          schoolId=SchoolClient.shared_high_school_id(),
                          courseCode='ALG-2',
                          letterGradeEarned='A',
                          numericGradeEarned=94)
