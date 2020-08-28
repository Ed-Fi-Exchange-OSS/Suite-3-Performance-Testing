# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from edfi_performance.api.client import EdFiAPIClient
from edfi_performance.api.client.school import SchoolClient


class CourseClient(EdFiAPIClient):
    endpoint = 'courses'


class CourseTranscriptClient(EdFiAPIClient):
    endpoint = 'courseTranscripts'

    dependencies = {
        'edfi_performance.api.client.student.StudentAcademicRecordClient': {
            'client_name': 'record_client',
        }
    }

    def create_with_dependencies(self, **kwargs):
        school_id = kwargs.pop('schoolId', SchoolClient.shared_elementary_school_id())

        record_reference = self.record_client.create_with_dependencies(schoolId=school_id)

        # Create course transcript
        transcript_attrs = self.factory.build_dict(
            courseReference__educationOrganizationId=school_id,
            studentAcademicRecordReference__educationOrganizationId=school_id,
            studentAcademicRecordReference__studentUniqueId=record_reference['attributes']['studentReference']
            ['studentUniqueId'],
            **kwargs
        )
        transcript_id = self.create(**transcript_attrs)

        return {
            'resource_id': transcript_id,
            'attributes': transcript_attrs,
            'dependency_ids': {
                'record_reference': record_reference
            }
        }

    def delete_with_dependencies(self, reference, **kwargs):
        self.delete(reference['resource_id'])
        self.record_client.delete_with_dependencies(reference['dependency_ids']['record_reference'])
