# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from edfi_performance_test.factories.utils import formatted_date
from edfi_performance_test.tasks.pipeclean.ed_fi_pipeclean_test_base import (
    EdFiPipecleanTestBase,
)


class GradebookEntryPipecleanTest(EdFiPipecleanTestBase):
    # This is an allowed natural key update
    update_attribute_name = "dateAssigned"
    update_attribute_value = formatted_date(3, 3)
