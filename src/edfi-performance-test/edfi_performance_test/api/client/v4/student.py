# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from typing import Dict

from edfi_performance_test.api.client.ed_fi_api_client import EdFiAPIClient
from edfi_performance_test.factories.utils import formatted_date
from edfi_performance_test.api.client.student import (
    StudentSectionAssociationClient,
)


class StudentGradebookEntryClientV4(EdFiAPIClient):
    endpoint = "studentGradebookEntries"

    dependencies: Dict = {
        StudentSectionAssociationClient: {"client_name": "assoc_client"},
        "edfi_performance_test.api.client.v4.gradebook_entries.GradebookEntryClientV4": {
            "client_name": "entry_client",
        },
    }

    def create_with_dependencies(self, **kwargs):
        # Create a student and section
        student_section_reference = self.assoc_client.create_with_dependencies()
        section_kwargs = {
            "sectionIdentifier": student_section_reference["attributes"][
                "sectionReference"
            ]["sectionIdentifier"],
            "localCourseCode": student_section_reference["attributes"][
                "sectionReference"
            ]["localCourseCode"],
            "schoolId": student_section_reference["attributes"]["sectionReference"][
                "schoolId"
            ],
            "schoolYear": student_section_reference["attributes"]["sectionReference"][
                "schoolYear"
            ],
            "sessionName": student_section_reference["attributes"]["sectionReference"][
                "sessionName"
            ],
        }

        # Create gradebook entry
        entry_id, title = self.entry_client.create(
            unique_id_field="title", sectionReference=section_kwargs
        )

        # Create student gradebook entry
        entry_attrs = dict(
            gradebookEntryTitle=title,
            dateAssigned=formatted_date(2, 2),
            **section_kwargs
        )

        assoc_attrs = dict(
            studentUniqueId=student_section_reference["attributes"]["studentReference"][
                "studentUniqueId"
            ],
            beginDate=formatted_date(8, 23),
            **section_kwargs
        )

        return self.create_using_dependencies(
            [{"assoc_client": student_section_reference}, {"entry_client": entry_id}],
            gradebookEntryReference=entry_attrs,
            studentSectionAssociationReference=assoc_attrs,
        )

    def delete_with_dependencies(self, reference, **kwargs):
        self.delete_item(reference["resource_id"])
        dependencies = reference["dependency_ids"]
        self.entry_client.delete_item(dependencies["entry_client"])
        self.assoc_client.delete_with_dependencies(dependencies["assoc_client"])
