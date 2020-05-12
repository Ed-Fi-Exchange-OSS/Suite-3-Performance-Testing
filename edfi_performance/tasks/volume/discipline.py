from locust import task

from edfi_performance.api.client.school import SchoolClient
from edfi_performance.factories.descriptors.utils import build_descriptor
from edfi_performance.tasks.volume import EdFiVolumeTestBase


class DisciplineIncidentVolumeTest(EdFiVolumeTestBase):
    @task
    def run_discipline_incident_scenarios(self):
        self.run_scenario('reporterName', "Villa, Mark")
        self.run_scenario('incidentLocationDescriptor', build_descriptor('IncidentLocation', 'Classroom'),
                          schoolId=SchoolClient.shared_high_school_id(),  # Prepopulated school
                          behaviors__0__behaviorDescriptor=build_descriptor('Behavior', 'State Offense'),
                          incidentLocationDescriptor=build_descriptor('IncidentLocation', 'Library/media center'),
                          reporterName="Moran, Patricia")


class DisciplineActionVolumeTest(EdFiVolumeTestBase):
    @task
    def run_discipline_action_scenarios(self):
        self.run_scenario('disciplines',
                          [{'disciplineDescriptor': build_descriptor('Discipline', 'In School Suspension')}])
        self.run_scenario('disciplines',
                          [{'disciplineDescriptor': build_descriptor('Discipline', 'Community Service')}],
                          schoolId=SchoolClient.shared_high_school_id(),
                          disciplines__0__disciplineDescriptor=build_descriptor('Discipline', 'In School Suspension'),
                          actualDisciplineActionLength=5)
