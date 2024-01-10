# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import factory
import random

from edfi_performance_test.factories.resources.api_factory import APIFactory
from edfi_performance_test.factories.utils import RandomSuffixAttribute


class EvaluationRubricDimensionFactory(APIFactory):
    evaluationRubricRating = random.randint(1, 28)
    programEvaluationElementReference = factory.Dict(
        dict(
            programEducationOrganizationId=None,
            programEvaluationElementTitle=None,
            programEvaluationPeriodDescriptor=None,
            programEvaluationTitle=None,
            programEvaluationTypeDescriptor=None,
            programName=None,
            programTypeDescriptor=None
        )
    )
    evaluationCriterionDescription = RandomSuffixAttribute("Impact Analysis", suffix_length=10)
