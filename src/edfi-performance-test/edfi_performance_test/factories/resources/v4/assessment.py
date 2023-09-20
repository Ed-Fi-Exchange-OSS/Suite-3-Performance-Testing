# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import factory

from edfi_performance_test.factories.resources.api_factory import APIFactory
from edfi_performance_test.factories.descriptors.utils import build_descriptor
from edfi_performance_test.factories.utils import current_year
from edfi_performance_test.api.client.student import StudentClient


class StudentAssessmentEducationOrganizationAssociationFactory(APIFactory):
    educationOrganizationAssociationTypeDescriptor = build_descriptor(
        "EducationOrganizationAssociationType", "Administration"
    )
    educationOrganizationReference = factory.Dict(
        dict(educationOrganizationId=None)
    )
    schoolYearTypeReference = factory.Dict(dict(schoolYear=current_year()))
    studentAssessmentReference = factory.Dict(
        dict(
            assessmentIdentifier=None,
            namespace="uri://ed-fi.org/Assessment/Assessment.xml",
            studentAssessmentIdentifier=None,
            studentUniqueId=StudentClient.shared_student_id(),
        )
    )
