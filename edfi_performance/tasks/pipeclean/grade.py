# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from edfi_performance.tasks.pipeclean import EdFiPipecleanTestBase


class GradePipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = 'numericGradeEarned'
    update_attribute_value = 83
