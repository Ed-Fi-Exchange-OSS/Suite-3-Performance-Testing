# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# See the LICENSE and NOTICES files in the project root for more information.

from typing import Any, Dict, List

from locust import task

from edfi_performance_test.factories.resources.student import StudentFactory
from edfi_performance_test.factories.resources.section import SectionFactory
from edfi_performance_test.tasks.batch_volume.batch_volume_fixtures import (
    get_or_create_shared_school,
    get_or_create_shared_course_offering,
    get_or_create_shared_class_period,
    get_or_create_shared_location,
)
from edfi_performance_test.tasks.batch_volume.batch_volume_test_base import (
    BatchVolumeTestBase,
)


class MixedStudentSectionBatchVolumeTest(BatchVolumeTestBase):
    """
    Mixed-resource batch scenario that combines one student triple and one
    section triple into a single /batch request.

    Each batch contains:
    - 3 student operations: create, update, delete
    - 3 section operations: create, update, delete
    for a total of 6 operations per request.
    """

    # Provide a default resource/factory to satisfy BatchVolumeTestBase
    # initialization. These are not used directly for building mixed triples.
    resource: str = "students"
    factory: Any = StudentFactory

    def _student_natural_key(self, document: Dict[str, Any]) -> Dict[str, Any]:
        return {"studentUniqueId": document["studentUniqueId"]}

    def _student_update_document(self, document: Dict[str, Any]) -> Dict[str, Any]:
        updated = dict(document)
        updated["firstName"] = f"{document.get('firstName', 'Student')} Mixed"
        return updated

    def _section_natural_key(self, document: Dict[str, Any]) -> Dict[str, Any]:
        reference = document["courseOfferingReference"]
        return {
            "sectionIdentifier": document["sectionIdentifier"],
            "localCourseCode": reference["localCourseCode"],
            "schoolId": reference["schoolId"],
            "schoolYear": reference["schoolYear"],
            "sessionName": reference["sessionName"],
        }

    def _section_update_document(self, document: Dict[str, Any]) -> Dict[str, Any]:
        updated = dict(document)
        updated["sequenceOfCourse"] = document.get("sequenceOfCourse", 1) + 1
        return updated

    @task
    def run_mixed_batch(self) -> None:
        school = get_or_create_shared_school()
        course_offering = get_or_create_shared_course_offering()
        class_period = get_or_create_shared_class_period()
        location = get_or_create_shared_location()

        school_id = school["schoolId"]

        # Build student triple
        student_document = StudentFactory.build_dict()
        student_documents: List[Dict[str, Any]] = [student_document]
        student_operations = self.build_triple_operations(
            "students",
            student_documents,
            get_natural_key=self._student_natural_key,
            build_update_document=self._student_update_document,
        )

        # Build section triple wired to shared fixtures
        section_document = SectionFactory.build_dict()

        section_document["courseOfferingReference"] = {
            "localCourseCode": course_offering["localCourseCode"],
            "schoolId": course_offering["schoolId"],
            "schoolYear": course_offering["schoolYear"],
            "sessionName": course_offering["sessionName"],
        }

        section_document["classPeriods"] = [
            {
                "classPeriodReference": {
                    "classPeriodName": class_period["classPeriodName"],
                    "schoolId": class_period["schoolId"],
                }
            }
        ]

        section_document["locationReference"] = {
            "schoolId": location["schoolId"],
            "classroomIdentificationCode": location["classroomIdentificationCode"],
        }

        # Ensure the section references the shared school where appropriate.
        section_document["courseOfferingReference"]["schoolId"] = school_id

        section_documents: List[Dict[str, Any]] = [section_document]
        section_operations = self.build_triple_operations(
            "sections",
            section_documents,
            get_natural_key=self._section_natural_key,
            build_update_document=self._section_update_document,
        )

        operations = student_operations + section_operations
        if not operations:
            return

        self._batch_client.post_batch(
            operations, name="mixed-students-sections-batch-2"
        )

