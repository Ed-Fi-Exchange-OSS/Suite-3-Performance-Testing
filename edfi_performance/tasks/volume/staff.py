# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from locust import task

from edfi_performance.api.client.school import SchoolClient
from edfi_performance.factories.descriptors.utils import build_descriptor
from edfi_performance.factories.utils import formatted_date
from edfi_performance.tasks.volume import EdFiVolumeTestBase


class StaffEducationOrganizationAssignmentAssociationVolumeTest(EdFiVolumeTestBase):
    @task
    def run_association_scenarios(self):
        self.run_scenario('positionTitle', '2nd Grade Teacher')
        self.run_scenario('positionTitle', '2nd Grade Teacher',
                          educationOrganizationReference__educationOrganizationId=SchoolClient.shared_high_school_id(),
                          positionTitle='9th Grade Teacher')

    def _update_attribute(self, resource_id, resource_attrs, update_attribute_name, update_attribute_value, **kwargs):
        # Both scenarios remove endDate if present
        resource_attrs.pop('endDate', None)
        resource_attrs[update_attribute_name] = update_attribute_value
        self.update(resource_id, **resource_attrs)


class StaffVolumeTest(EdFiVolumeTestBase):
    @task
    def run_staff_scenarios(self):
        self.run_scenario('highlyQualifiedTeacher', False)
        self.run_scenario('hispanicLatinoEthnicity', False,
                          firstName="Jane",
                          middleName="Marcy",
                          lastSurname="Smith",
                          birthDate="1973-07-20",
                          highestCompletedLevelOfEducationDescriptor=build_descriptor('LevelOfEducation', 'Doctorate'),
                          personalTitlePrefix="Mrs",
                          sexDescriptor=build_descriptor('Sex', 'Female'),
                          electronicMails=[
                              dict(
                                  electronicMailAddress="janesmith@edficert.org",
                                  electronicMailTypeDescriptor=build_descriptor('ElectronicMailType', 'Work'),
                              )
                          ],
                          races__0__raceDescriptor=build_descriptor('Race', 'Black - African American'))


class StaffCohortAssociationVolumeTest(EdFiVolumeTestBase):
    @task
    def run_association_scenarios(self):
        self.run_scenario('endDate', '2014-12-10')
        self.run_scenario('endDate', '2014-12-10', schoolId=SchoolClient.shared_high_school_id())


class StaffSchoolAssociationVolumeTest(EdFiVolumeTestBase):
    @task
    def run_association_scenarios(self):
        self.run_scenario('academicSubjects',
                          [{'academicSubjectDescriptor': build_descriptor('AcademicSubject', 'Social Studies')}])
        self.run_scenario('gradeLevels', [{'gradeLevelDescriptor': build_descriptor('GradeLevel', 'Tenth grade')}],
                          schoolId=SchoolClient.shared_high_school_id())


class StaffSectionAssociationVolumeTest(EdFiVolumeTestBase):
    @task
    def run_association_scenarios(self):
        self.run_scenario('classroomPositionDescriptor', build_descriptor('ClassroomPosition', 'Assistant Teacher'))
        self.run_scenario('endDate', formatted_date(9, 1),
                          schoolId=SchoolClient.shared_high_school_id(),
                          courseCode="ALG-2")
