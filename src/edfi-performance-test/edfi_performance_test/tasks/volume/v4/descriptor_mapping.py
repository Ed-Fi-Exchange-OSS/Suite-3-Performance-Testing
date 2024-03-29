# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from edfi_performance_test.tasks.volume.ed_fi_volume_test_base import EdFiVolumeTestBase


class DescriptorMappingVolumeTest(EdFiVolumeTestBase):
    """
    This resource has no non-identity attributes.
    So we'll just verify that the PUT endpoint works without actually changing any attributes
    """
    def _touch_put_endpoint(self, resource_id, default_attributes):
        self.update(resource_id, **default_attributes)
