# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from edfi_performance.factories.descriptors.utils import build_descriptor
from edfi_performance.tasks.pipeclean import EdFiPipecleanTestBase


class PostSecondaryInstitutionPipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = 'nameOfInstitution'
    update_attribute_value = "University of Texas - Austin"


class PostSecondaryEventPipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = 'postSecondaryEventCategoryDescriptor'
    update_attribute_value = build_descriptor('PostSecondaryEventCategory', 'College Degree Received')
