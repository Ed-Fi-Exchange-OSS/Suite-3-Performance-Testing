# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from typing import Dict

from edfi_performance_test.api.client.ed_fi_api_client import EdFiAPIClient
from edfi_performance_test.api.client.school import SchoolClient
from edfi_performance_test.api.client.student import StudentSectionAssociationClient


class GradeClient(EdFiAPIClient):
    endpoint = 'grades'

    dependencies: Dict = {
        StudentSectionAssociationClient: {
            'client_name': 'section_assoc_client',
        }
    }

    def create_with_dependencies(self, **kwargs):
        school_id = kwargs.pop('schoolId', SchoolClient.shared_elementary_school_id())
        course_code = kwargs.pop('courseCode', 'ELA-01')

        assoc_reference = self.section_assoc_client.create_with_dependencies(schoolId=school_id, courseCode=course_code)
        grade_period = \
            assoc_reference['dependency_ids']['section_client']['gradingPeriods'][0]['gradingPeriodReference']
        section_reference = assoc_reference['attributes']['sectionReference']

        return self.create_using_dependencies(
            assoc_reference,
            gradingPeriodReference__schoolId=school_id,
            gradingPeriodReference__periodSequence=grade_period['periodSequence'],
            gradingPeriodReference__gradingPeriodDescriptor=grade_period['gradingPeriodDescriptor'],
            gradingPeriodReference__schoolYear=section_reference['schoolYear'],
            studentSectionAssociationReference__sectionIdentifier=section_reference['sectionIdentifier'],
            studentSectionAssociationReference__beginDate=assoc_reference['attributes']['beginDate'],
            studentSectionAssociationReference__studentUniqueId=
            assoc_reference['attributes']['studentReference']['studentUniqueId'],
            studentSectionAssociationReference__localCourseCode=section_reference['localCourseCode'],
            studentSectionAssociationReference__schoolId=section_reference['schoolId'],
            studentSectionAssociationReference__schoolYear=section_reference['schoolYear'],
            studentSectionAssociationReference__sessionName=section_reference['sessionName'],
            **kwargs
        )
