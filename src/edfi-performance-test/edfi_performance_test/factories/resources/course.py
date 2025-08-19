# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import factory

from edfi_performance_test.api.client.education import LocalEducationAgencyClient
from edfi_performance_test.api.client.school import SchoolClient
from edfi_performance_test.factories.resources.api_factory import APIFactory
from edfi_performance_test.factories.descriptors.utils import (
    build_descriptor,
    build_descriptor_dicts,
)
from edfi_performance_test.factories.utils import RandomSuffixAttribute, current_year


class CourseFactory(APIFactory):
    educationOrganizationReference = factory.Dict(
        dict(
            educationOrganizationId=LocalEducationAgencyClient.shared_education_organization_id()
        )
    )
    academicSubjectDescriptor = build_descriptor("AcademicSubject", "Mathematics")
    courseTitle = "Algebra I"
    courseCode = RandomSuffixAttribute("03100500")
    numberOfParts = 1
    identificationCodes = factory.LazyAttribute(
        lambda o: build_descriptor_dicts(
            "CourseIdentificationSystem",
            [("State course code", {"identificationCode": o.courseCode})],
        )
    )
    levelCharacteristics = factory.List(
        [
            factory.Dict(
                dict(
                    courseLevelCharacteristicDescriptor=build_descriptor(
                        "CourseLevelCharacteristic", "Core Subject"
                    )
                )
            ),
        ]
    )


class CourseTranscriptFactory(APIFactory):
    courseReference = factory.Dict(
        dict(
            educationOrganizationId=SchoolClient.shared_elementary_school_id(),  # Prepopulated school
            courseCode="ELA-01",
        ),
    )
    studentAcademicRecordReference = factory.Dict(
        dict(
            educationOrganizationId=SchoolClient.shared_elementary_school_id(),
            schoolYear=current_year(),
            studentUniqueId=111111,  # Default value for scenarios, but not in DB
            termDescriptor=build_descriptor("Term", "Fall Semester"),
        ),
    )
    courseAttemptResultDescriptor = build_descriptor("CourseAttemptResult", "Pass")
    finalLetterGradeEarned = "B"
    finalNumericGradeEarned = 83
