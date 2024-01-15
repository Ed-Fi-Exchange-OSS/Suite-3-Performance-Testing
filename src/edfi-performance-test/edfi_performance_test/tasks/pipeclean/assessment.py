# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from edfi_performance_test.tasks.pipeclean.ed_fi_pipeclean_test_base import (
    EdFiPipecleanTestBase,
)


class AssessmentPipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = "title"
    update_attribute_value = "AP English 3"


class AssessmentItemPipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = "correctResponse"
    update_attribute_value = "C"


class LearningObjectivePipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = "description"
    update_attribute_value = (
        "The student will demonstrate the ability to utilize numbers to perform"
        " operations with complex concepts at a high level."
    )


class LearningStandardPipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = "courseTitle"
    update_attribute_value = "Advanced Math for students v4.6"


class ObjectiveAssessmentPipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = "maxRawScore"
    update_attribute_value = 10
