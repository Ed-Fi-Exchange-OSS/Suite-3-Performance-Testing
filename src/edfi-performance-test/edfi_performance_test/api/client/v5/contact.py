# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from edfi_performance_test.api.client.ed_fi_api_client import EdFiAPIClient
from edfi_performance_test.api.client.school import SchoolClient


class ContactClient(EdFiAPIClient):
    endpoint = "contacts"

    dependencies = {
        "edfi_performance_test.api.client.v5.student.StudentContactAssociationClient": {
            "client_name": "contact_assoc_client",
        },
        "edfi_performance_test.api.client.student.StudentClient": {},
    }

    _contact_id = None

    def create_with_dependencies(self, **kwargs):
        school_id = kwargs.pop("schoolId", SchoolClient.shared_elementary_school_id())

        # Create contact
        contact_attrs = self.factory.build_dict(**kwargs)
        contact_unique_id = contact_attrs["contactUniqueId"]
        contact_id = self.create(**contact_attrs)

        # Create enrolled student
        student_reference = self.student_client.create_with_dependencies(
            schoolId=school_id
        )

        # Associate contact with student to allow updates
        assoc_id = self.contact_assoc_client.create(
            contactReference__contactUniqueId=contact_unique_id,
            studentReference__studentUniqueId=student_reference["attributes"][
                "studentUniqueId"
            ],
        )

        return {
            "resource_id": contact_id,
            "dependency_ids": {
                "assoc_id": assoc_id,
                "student_reference": student_reference,
            },
            "attributes": contact_attrs,
        }

    def delete_with_dependencies(self, reference, **kwargs):
        self.contact_assoc_client.delete_item(reference["dependency_ids"]["assoc_id"])
        self.student_client.delete_with_dependencies(
            reference["dependency_ids"]["student_reference"]
        )
        self.delete_item(reference["resource_id"])

    @classmethod
    def shared_contact_id(cls):
        if cls._contact_id is not None:
            return cls._contact_id
        cls._contact_id = cls.create_shared_resource("contactUniqueId")
        return cls._contact_id
