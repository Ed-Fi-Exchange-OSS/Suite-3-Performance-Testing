# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from edfi_performance_test.factories.descriptors.utils import build_descriptor
from edfi_performance_test.tasks.pipeclean.ed_fi_pipeclean_test_base import EdFiPipecleanTestBase


class DisciplineIncidentPipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = 'reporterName'
    update_attribute_value = "Villa, Mark"


class DisciplineActionPipecleanTest(EdFiPipecleanTestBase):
    def _touch_put_endpoint(self, resource_id, attrs):
        attrs['disciplines'][0]['disciplineDescriptor'] = build_descriptor('Discipline', 'In School Suspension')
        self.update(resource_id, **attrs)
