# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import factory

from edfi_performance_test.factories.resources.api_factory import APIFactory
from edfi_performance_test.factories.descriptors.utils import build_descriptor
from edfi_performance_test.factories.utils import RandomSuffixAttribute
from edfi_performance_test.api.client.education import LocalEducationAgencyClient
from edfi_performance_test.api.client.program import ProgramClient


class ProgramEvaluationFactory(APIFactory):
    programEvaluationPeriodDescriptor = build_descriptor("ProgramEvaluationPeriod", "End of Year")
    programEvaluationTitle = RandomSuffixAttribute("Program Evaluation", suffix_length=10)
    programEvaluationTypeDescriptor = build_descriptor("ProgramEvaluationType", "Observation")
    programReference = factory.Dict(
        dict(
            educationOrganizationId=LocalEducationAgencyClient.shared_education_organization_id(),
            programName=ProgramClient.shared_program_name(),
            programTypeDescriptor=build_descriptor(
                "ProgramType", ProgramClient.shared_program_name()
            ),
        )
    )
    evaluationMaxNumericRating = 3


class ProgramEvaluationElementFactory(APIFactory):
    programEvaluationElementTitle = RandomSuffixAttribute("Evaluation Element", suffix_length=10)
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
    elementMaxNumericRating = 2


class ProgramEvaluationObjetiveFactory(APIFactory):
    programEvaluationObjectiveTitle = RandomSuffixAttribute("Evaluation Objetive", suffix_length=10)
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
    objectiveMaxNumericRating = 4
