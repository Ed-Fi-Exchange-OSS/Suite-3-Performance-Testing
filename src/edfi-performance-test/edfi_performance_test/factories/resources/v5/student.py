# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import factory

from edfi_performance_test.factories.resources.api_factory import APIFactory
from edfi_performance_test.factories.descriptors.utils import build_descriptor
from edfi_performance_test.factories.utils import (
    RandomDateAttribute
)
from edfi_performance_test.api.client.education import LocalEducationAgencyClient


class StudentContactAssociationFactory(APIFactory):
    studentReference = factory.Dict(
        dict(studentUniqueId=None)
    )
    contactReference = factory.Dict(dict(contactUniqueId=None))  # Must be entered by user
    emergencyContactStatus = True
    primaryContactStatus = True
    relationDescriptor = build_descriptor("Relation", "Father")


class StudentProgramEvaluationFactory(APIFactory):
    evaluationDate = RandomDateAttribute()
    programEvaluationReference = factory.Dict(
        dict(
           programEducationOrganizationId=None,
           programEvaluationPeriodDescriptor=None,
           programEvaluationTitle=None,
           programEvaluationTypeDescriptor=None,
           programName=None,
           programTypeDescriptor=None
        )
    )
    studentReference = factory.Dict(
        dict(studentUniqueId=None)
    )
    evaluationDuration = 60


class StudentSpecialEducationProgramEligibilityAssociationFactory(APIFactory):
    consentToEvaluationReceivedDate = RandomDateAttribute()
    educationOrganizationReference = factory.Dict(
        dict(educationOrganizationId=LocalEducationAgencyClient.shared_education_organization_id())
    )
    programReference = factory.Dict(
        dict(
            educationOrganizationId=LocalEducationAgencyClient.shared_education_organization_id(),
            programName=None,
            programTypeDescriptor=None,
        )
    )
    studentReference = factory.Dict(
        dict(studentUniqueId=111111)
    )
    evaluationCompleteIndicator = False
    ideaPartDescriptor = build_descriptor("IdeaPart", "IDEA Part B")
