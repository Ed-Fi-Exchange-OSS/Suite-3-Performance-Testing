# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from edfi_performance.api.client import EdFiAPIClient
from edfi_performance.api.client.section import SectionClient


class GradebookEntryClient(EdFiAPIClient):
    endpoint = 'gradebookEntries'

    dependencies = {
        SectionClient: {},
    }

    def create_with_dependencies(self, **kwargs):
        section_reference = self.section_client.create_with_dependencies()
        section_attrs = section_reference['attributes']

        entry_attrs = self.factory.build_dict(
            sectionReference__sectionIdentifier=section_attrs['sectionIdentifier'],
            sectionReference__localCourseCode=section_attrs['courseOfferingReference']['localCourseCode'],
            sectionReference__schoolId=section_attrs['courseOfferingReference']['schoolId'],
            sectionReference__schoolYear=section_attrs['courseOfferingReference']['schoolYear'],
            sectionReference__sessionName=section_attrs['courseOfferingReference']['sessionName'],
        )
        entry_id = self.create(**entry_attrs)

        return {
            'resource_id': entry_id,
            'dependency_ids': {
                'section_reference': section_reference,
            },
            'attributes': entry_attrs,
        }

    def delete_with_dependencies(self, reference, **kwargs):
        self.delete(reference['resource_id'])
        self.section_client.delete_with_dependencies(reference['dependency_ids']['section_reference'])

