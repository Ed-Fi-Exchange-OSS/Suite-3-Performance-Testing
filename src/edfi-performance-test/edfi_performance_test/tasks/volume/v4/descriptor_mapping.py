# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from edfi_performance_test.tasks.volume.ed_fi_volume_test_base import EdFiVolumeTestBase


class DescriptorMappingVolumeTest(EdFiVolumeTestBase):
    def _update_attribute(
        self,
        resource_id,
        resource_attrs,
        update_attribute_name,
        update_attribute_value,
        **kwargs
    ):
        # all endpoints fields are required - just test PUT path works
        self.update(resource_id, **resource_attrs)
