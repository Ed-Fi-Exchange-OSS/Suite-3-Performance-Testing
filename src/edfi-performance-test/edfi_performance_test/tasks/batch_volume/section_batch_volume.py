# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# See the LICENSE and NOTICES files in the project root for more information.

from typing import Any, Dict, List

from locust import task

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


class SectionBatchVolumeTest(BatchVolumeTestBase):
    """
    Batch volume scenario for the sections resource.

    For each logical record, this scenario issues a create, update, and delete
    in a single batch request. The update and delete operations target the
    section via its natural key (sectionIdentifier + courseOffering reference).
    """

    resource: str = "sections"
    factory: Any = SectionFactory

    def get_natural_key(self, document: Dict[str, Any]) -> Dict[str, Any]:
        reference = document["courseOfferingReference"]
        return {
            "sectionIdentifier": document["sectionIdentifier"],
            "localCourseCode": reference["localCourseCode"],
            "schoolId": reference["schoolId"],
            "schoolYear": reference["schoolYear"],
            "sessionName": reference["sessionName"],
        }

    def build_update_document(self, document: Dict[str, Any]) -> Dict[str, Any]:
        updated = dict(document)
        updated["sequenceOfCourse"] = document.get("sequenceOfCourse", 1) + 1
        return updated

    @task
    def run_section_batch(self) -> None:
        school = get_or_create_shared_school()
        course_offering = get_or_create_shared_course_offering()
        class_period = get_or_create_shared_class_period()
        location = get_or_create_shared_location()

        school_id = school["schoolId"]

        documents: List[Dict[str, Any]] = []
        for _ in range(self._batch_triple_count):
            doc = self.factory.build_dict()

            # Ensure references to shared fixtures for courseOffering, classPeriod, and location.
            doc["courseOfferingReference"] = {
                "localCourseCode": course_offering["localCourseCode"],
                "schoolId": course_offering["schoolId"],
                "schoolYear": course_offering["schoolYear"],
                "sessionName": course_offering["sessionName"],
            }

            doc["classPeriods"] = [
                {
                    "classPeriodReference": {
                        "classPeriodName": class_period["classPeriodName"],
                        "schoolId": class_period["schoolId"],
                    }
                }
            ]

            doc["locationReference"] = {
                "schoolId": location["schoolId"],
                "classroomIdentificationCode": location["classroomIdentificationCode"],
            }

            # Ensure the section references the shared school in any direct schoolId fields.
            doc["courseOfferingReference"]["schoolId"] = school_id

            documents.append(doc)

        self.run_triple_batch(self.resource, documents)

