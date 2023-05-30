# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from edfi_performance_test.factories.utils import RandomSuffixAttribute
from edfi_performance_test.tasks.pipeclean.ed_fi_pipeclean_test_base import (
    EdFiPipecleanTestBase,
)


class ClassPeriodPipecleanTest(EdFiPipecleanTestBase):
    # This is an allowed natural key update, which should automatically cascade through the API without error
    update_attribute_name = "classPeriodName"
    update_attribute_value = RandomSuffixAttribute("Class Period 01", suffix_length=10)
