# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from typing import Dict
from edfi_performance_test.api.client.ed_fi_api_client import EdFiAPIClient
from edfi_performance_test.api.client.school import SchoolClient


class CourseClient(EdFiAPIClient):
    endpoint = 'courses'


class CourseTranscriptClient(EdFiAPIClient):
    endpoint = 'courseTranscripts'

    dependencies: Dict = {
        'edfi_performance_test.api.client.student.StudentAcademicRecordClient': {
            'client_name': 'record_client',
        }
    }

    def create_with_dependencies(self, **kwargs):
        school_id = kwargs.pop('schoolId', SchoolClient.shared_elementary_school_id())

        record_reference = self.record_client.create_with_dependencies(schoolId=school_id)

        # Create course transcript
        return self.create_using_dependencies(
            record_reference,
            courseReference__educationOrganizationId=school_id,
            studentAcademicRecordReference__educationOrganizationId=school_id,
            studentAcademicRecordReference__studentUniqueId=record_reference['attributes']['studentReference']
            ['studentUniqueId'],
            **kwargs
        )
