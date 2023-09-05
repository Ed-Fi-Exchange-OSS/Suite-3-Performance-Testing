# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import factory

from edfi_performance_test.factories.resources.api_factory import APIFactory
from edfi_performance_test.factories.descriptors.utils import build_descriptor
from edfi_performance_test.factories.utils import (
    UniqueIdAttribute,
)


class LearningStandardFactoryV5(APIFactory):
    learningStandardId = UniqueIdAttribute()
    academicSubjects = factory.List(
        [
            factory.Dict(
                dict(
                    academicSubjectDescriptor=build_descriptor(
                        "AcademicSubject", "Mathematics"
                    )
                )
            )
        ]
    )
    courseTitle = "Advanced Math for students v4.4"
    description = "Unit 1 Advanced Math for students v4.4"
    namespace = "uri://ed-fi.org/LearningStandard/LearningStandard.xml"
    gradeLevels = factory.List(
        [
            factory.Dict(
                dict(gradeLevelDescriptor=build_descriptor("GradeLevel", "Tenth grade"))
            ),
        ]
    )
    contentStandard = factory.Dict(
        dict(
            title="Content Standard Demo",
        )
    )
