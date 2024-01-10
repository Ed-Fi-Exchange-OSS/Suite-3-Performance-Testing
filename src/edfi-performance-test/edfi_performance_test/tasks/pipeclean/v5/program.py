# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from edfi_performance_test.tasks.pipeclean.ed_fi_pipeclean_test_base import (
    EdFiPipecleanTestBase,
)


class ProgramEvaluationPipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = "evaluationMaxNumericRating"
    update_attribute_value = 7


class ProgramEvaluationElementPipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = "elementMaxNumericRating"
    update_attribute_value = 5


class ProgramEvaluationObjetivePipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = "objectiveSortOrder"
    update_attribute_value = 1
