# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# See the LICENSE and NOTICES files in the project root for more information.

from typing import Any, Dict, List

from locust import task

from edfi_performance_test.tasks.batch_volume.batch_volume_test_base import (
    BatchVolumeTestBase,
)


class StudentBatchVolumeTest(BatchVolumeTestBase):
    """
    Batch volume scenario for the students resource.

    For each logical record, this scenario issues a create, update, and delete
    in a single batch request. The update and delete operations target the
    student via natural key (studentUniqueId).
    """

    resource: str = "students"
    factory: Any = None

    def __init__(self, parent, *args, **kwargs):
        # Lazy import of StudentFactory to avoid importing EdFi clients and
        # Locust-heavy dependencies during module import, which simplifies
        # unit testing.
        from edfi_performance_test.factories.resources.student import StudentFactory

        self.factory = StudentFactory
        super().__init__(parent, *args, **kwargs)

    def get_natural_key(self, document: Dict[str, Any]) -> Dict[str, Any]:
        return {"studentUniqueId": document["studentUniqueId"]}

    def build_update_document(self, document: Dict[str, Any]) -> Dict[str, Any]:
        updated = dict(document)
        updated["firstName"] = f"{document.get('firstName', 'Student')} Updated"
        return updated

    @task
    def run_student_batch(self) -> None:
        from edfi_performance_test.tasks.batch_volume.batch_volume_fixtures import (
            get_or_create_shared_school,
        )

        school = get_or_create_shared_school()
        _school_id = school["schoolId"]

        documents: List[Dict[str, Any]] = []
        for _ in range(self._batch_triple_count):
            doc = self.factory.build_dict()
            # Ensure the student is associated with the shared school.
            doc.setdefault("studentEducationOrganizationAssociations", [])
            documents.append(doc)

        self.run_triple_batch(self.resource, documents)
