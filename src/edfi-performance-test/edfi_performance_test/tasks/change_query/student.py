# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from edfi_performance_test.tasks.change_query.ed_fi_change_query_test_base import (
    EdFiChangeQueryTestBase,
)


class StudentChangeQueryTest(EdFiChangeQueryTestBase):
    endpoint = "students"


class StudentSectionAssociationChangeQueryTest(EdFiChangeQueryTestBase):
    endpoint = "studentSectionAssociations"


class StudentSectionAttendanceEventChangeQueryTest(EdFiChangeQueryTestBase):
    endpoint = "studentSectionAttendanceEvents"


class StudentEducationOrganizationAssociationChangeQueryTest(EdFiChangeQueryTestBase):
    endpoint = "studentEducationOrganizationAssociations"
