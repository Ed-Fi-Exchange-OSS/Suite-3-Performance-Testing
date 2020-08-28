# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from edfi_performance.factories.descriptors.utils import build_descriptor
from edfi_performance.factories.utils import formatted_date
from edfi_performance.tasks.pipeclean import EdFiPipecleanTestBase


class OpenStaffPositionPipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = 'datePosted'
    update_attribute_value = formatted_date(3, 31)


class StaffPipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = 'highlyQualifiedTeacher'
    update_attribute_value = False


class StaffAbsenceEventPipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = 'absenceEventReason'
    update_attribute_value = "Vacationing in Fiji"


class StaffCohortAssociationPipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = 'endDate'
    update_attribute_value = '2014-12-10'


class StaffEducationOrganizationAssignmentAssociationPipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = 'positionTitle'
    update_attribute_value = "2nd Grade Teacher"


class StaffEducationOrganizationContactAssociationPipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = 'electronicMailAddress'
    update_attribute_value = "staff@elementary-school.edu"


class StaffEducationOrganizationEmploymentAssociationPipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = 'hourlyWage'
    update_attribute_value = 25.0


class StaffLeavePipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = 'reason'
    update_attribute_value = "Extended family emergency"


class StaffProgramAssociationPipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = 'studentRecordAccess'
    update_attribute_value = False


class StaffSchoolAssociationPipecleanTest(EdFiPipecleanTestBase):
    def _touch_put_endpoint(self, resource_id, default_attributes):
        default_attributes['academicSubjects'].append(
            dict(academicSubjectDescriptor=build_descriptor('AcademicSubject', 'Social Studies'))
        )
        self.update(resource_id, **default_attributes)


class StaffSectionAssociationPipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = 'classroomPositionDescriptor'
    update_attribute_value = build_descriptor('ClassroomPosition', 'Assistant Teacher')
