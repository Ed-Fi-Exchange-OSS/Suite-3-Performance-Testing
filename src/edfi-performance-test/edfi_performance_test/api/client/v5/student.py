# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from typing import Dict

from edfi_performance_test.api.client.ed_fi_api_client import EdFiAPIClient
from edfi_performance_test.api.client.v5.contact import ContactClient


class StudentContactAssociationClient(EdFiAPIClient):
    endpoint = "studentContactAssociations"

    dependencies: Dict = {
        "edfi_performance_test.api.client.student.StudentClient": {},
    }

    def create_with_dependencies(self, **kwargs):
        # Create enrolled student
        student_reference = self.student_client.create_with_dependencies()

        # Create contact
        contact_unique_id = kwargs.pop("contactUniqueId", ContactClient.shared_contact_id())

        # Create contact - student association
        return self.create_using_dependencies(
            student_reference,
            studentReference__studentUniqueId=student_reference["attributes"][
                "studentUniqueId"
            ],
            contactReference__contactUniqueId=contact_unique_id,
            **kwargs
        )
