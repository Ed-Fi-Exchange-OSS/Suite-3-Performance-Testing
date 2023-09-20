# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from edfi_performance_test.tasks.pipeclean.ed_fi_pipeclean_test_base import (
    EdFiPipecleanTestBase,
)
from edfi_performance_test.api.client.school import SchoolClient


class StudentAssessmentEducationOrganizationAssociationPipecleanTest(EdFiPipecleanTestBase):
    def _touch_put_endpoint(self, resource_id, default_attributes):
        default_attributes["educationOrganizationReference"][
            "educationOrganizationId"
        ] = SchoolClient.shared_elementary_school_id()
        self.update(resource_id, **default_attributes)
