# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from edfi_performance_test.api.client.ed_fi_api_client import EdFiAPIClient
from edfi_performance_test.api.client.school import SchoolClient


class CourseOfferingClient(EdFiAPIClient):
    endpoint = 'courseOfferings'

    dependencies = {
        'edfi_performance_test.api.client.session.SessionClient': {}
    }

    def create_with_dependencies(self, **kwargs):
        school_id = kwargs.pop('schoolId', SchoolClient.shared_elementary_school_id())

        session_reference = self.session_client.create_with_dependencies(schoolId=school_id)

        return self.create_using_dependencies(
            session_reference,
            sessionReference__schoolId=school_id,
            sessionReference__schoolYear=2014,
            sessionReference__sessionName=session_reference['attributes']['sessionName'],
            **kwargs
        )
