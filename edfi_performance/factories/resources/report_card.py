# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import factory

from edfi_performance.api.client.education import LocalEducationAgencyClient
from edfi_performance.api.client.school import SchoolClient
from edfi_performance.api.client.student import StudentClient
from edfi_performance.factories import APIFactory
from edfi_performance.factories.descriptors.utils import build_descriptor


class ReportCardFactory(APIFactory):
    educationOrganizationReference = factory.Dict(dict(educationOrganizationId=LocalEducationAgencyClient.shared_education_organization_id()))
    studentReference = factory.Dict(dict(studentUniqueId=StudentClient.shared_student_id()))  # Prepopulated student
    gradingPeriodReference = factory.Dict(
        dict(
            periodSequence=None,  # Must be created
            schoolId=SchoolClient.shared_elementary_school_id(),
            schoolYear=2014,
            gradingPeriodDescriptor=build_descriptor("GradingPeriod", "First Six Weeks"),
        )
    )
    gpaGivenGradingPeriod = 3.14
