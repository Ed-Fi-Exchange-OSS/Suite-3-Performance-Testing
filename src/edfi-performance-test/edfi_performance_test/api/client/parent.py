# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from edfi_performance_test.api.client.ed_fi_api_client import EdFiAPIClient
from edfi_performance_test.api.client.school import SchoolClient


class ParentClient(EdFiAPIClient):
    endpoint = "parents"

    dependencies = {
        "edfi_performance_test.api.client.student.StudentParentAssociationClient": {
            "client_name": "parent_assoc_client",
        },
        "edfi_performance_test.api.client.student.StudentClient": {},
    }

    _parent_id = None

    def create_with_dependencies(self, **kwargs):
        school_id = kwargs.pop("schoolId", SchoolClient.shared_elementary_school_id())

        # Create parent
        parent_attrs = self.factory.build_dict(**kwargs)
        parent_unique_id = parent_attrs["parentUniqueId"]
        parent_id = self.create(**parent_attrs)

        # Create enrolled student
        student_reference = self.student_client.create_with_dependencies(
            schoolId=school_id
        )

        # Associate parent with student to allow updates
        assoc_id = self.parent_assoc_client.create(
            parentReference__parentUniqueId=parent_unique_id,
            studentReference__studentUniqueId=student_reference["attributes"][
                "studentUniqueId"
            ],
        )

        return {
            "resource_id": parent_id,
            "dependency_ids": {
                "assoc_id": assoc_id,
                "student_reference": student_reference,
            },
            "attributes": parent_attrs,
        }

    def delete_with_dependencies(self, reference, **kwargs):
        self.parent_assoc_client.delete(reference["dependency_ids"]["assoc_id"])
        self.student_client.delete_with_dependencies(
            reference["dependency_ids"]["student_reference"]
        )
        self.delete_item(reference["resource_id"])

    @classmethod
    def shared_parent_id(cls):
        if cls._parent_id is not None:
            return cls._parent_id
        cls._parent_id = cls.create_shared_resource("parentUniqueId")
        return cls._parent_id
