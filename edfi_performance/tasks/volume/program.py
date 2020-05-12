from locust import task

from edfi_performance.tasks.volume import EdFiVolumeTestBase


class ProgramVolumeTest(EdFiVolumeTestBase):
    @task
    def run_program_scenario(self):
        self.run_scenario()
