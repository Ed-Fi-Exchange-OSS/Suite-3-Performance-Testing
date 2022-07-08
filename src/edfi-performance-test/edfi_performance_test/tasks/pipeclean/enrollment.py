# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from edfi_performance_test.tasks.pipeclean.composite import (
    EdFiCompositePipecleanTestBase,
)

enrollment_composite_resources = [
    "localEducationAgencies",
    "schools",
    "sections",
    "staffs",
    "students",
]


class LocalEducationAgencyEnrollmentCompositePipecleanTest(
    EdFiCompositePipecleanTestBase
):
    def _run_pipeclean_scenario(self):
        self.run_get_only_pipeclean_scenario()


class SchoolEnrollmentCompositePipecleanTest(EdFiCompositePipecleanTestBase):
    composite_resources = enrollment_composite_resources


class SectionEnrollmentCompositePipecleanTest(EdFiCompositePipecleanTestBase):
    composite_resources = enrollment_composite_resources


class StaffEnrollmentCompositePipecleanTest(EdFiCompositePipecleanTestBase):
    composite_resources = enrollment_composite_resources


class StudentEnrollmentCompositePipecleanTest(EdFiCompositePipecleanTestBase):
    composite_resources = enrollment_composite_resources
