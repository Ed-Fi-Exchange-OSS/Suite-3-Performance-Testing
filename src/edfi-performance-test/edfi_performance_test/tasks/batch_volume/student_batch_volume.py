# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# See the LICENSE and NOTICES files in the project root for more information.

import logging
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
    logger = logging.getLogger("locust.runners")

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
        for index in range(self._batch_triple_count):
            doc = self.factory.build_dict()
            # Ensure the student is associated with the shared school.
            doc.setdefault("studentEducationOrganizationAssociations", [])
            # Log the natural key for debugging identity-conflict issues.
            try:
                student_unique_id = doc["studentUniqueId"]
            except KeyError:
                student_unique_id = "<missing>"
            # Use error level so that these diagnostics are visible even when
            # running with higher log thresholds during debugging.
            self.logger.error(
                "StudentBatchVolumeTest: preparing triple %s with studentUniqueId=%s",
                index,
                student_unique_id,
            )
            documents.append(doc)

        self.run_triple_batch(self.resource, documents)
