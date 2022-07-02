# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from edfi_performance_test.tasks.pipeclean.ed_fi_pipeclean_test_base import EdFiPipecleanTestBase


class CoursePipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = 'courseTitle'
    update_attribute_value = "Algebra II"


class CourseTranscriptPipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = 'finalNumericGradeEarned'
    update_attribute_value = 87
