# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from edfi_performance_test.tasks.pipeclean.ed_fi_pipeclean_test_base import (
    EdFiPipecleanTestBase,
)


class PostSecondaryInstitutionPipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = "nameOfInstitution"
    update_attribute_value = "University of Texas - Austin"


class PostSecondaryEventPipecleanTest(EdFiPipecleanTestBase):
    # all endpoints fields are required - just test PUT path works
    def _touch_put_endpoint(self, resource_id, default_attributes):
        self.update(resource_id, **default_attributes)
