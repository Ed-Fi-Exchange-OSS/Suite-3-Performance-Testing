# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from typing import Dict
from edfi_performance_test.api.client.ed_fi_api_client import EdFiAPIClient
from edfi_performance_test.api.client.section import SectionClient


class GradebookEntryClient(EdFiAPIClient):
    endpoint = "gradebookEntries"

    dependencies: Dict = {
        SectionClient: {},
    }

    def create_with_dependencies(self, **kwargs):
        section_reference = self.section_client.create_with_dependencies()
        section_attrs = section_reference["attributes"]

        return self.create_using_dependencies(
            section_reference,
            sectionReference__sectionIdentifier=section_attrs["sectionIdentifier"],
            sectionReference__localCourseCode=section_attrs["courseOfferingReference"][
                "localCourseCode"
            ],
            sectionReference__schoolId=section_attrs["courseOfferingReference"][
                "schoolId"
            ],
            sectionReference__schoolYear=section_attrs["courseOfferingReference"][
                "schoolYear"
            ],
            sectionReference__sessionName=section_attrs["courseOfferingReference"][
                "sessionName"
            ],
        )
