# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import factory

from edfi_performance.api.client.education import LocalEducationAgencyClient
from edfi_performance.factories import APIFactory
from edfi_performance.factories.descriptors.utils import build_descriptor
from edfi_performance.factories.utils import UniqueIdAttribute


class CompetencyObjectiveFactory(APIFactory):
    educationOrganizationReference = factory.Dict(dict(educationOrganizationId=LocalEducationAgencyClient.shared_education_organization_id()))
    objective = UniqueIdAttribute(num_chars=60)
    objectiveGradeLevelDescriptor = build_descriptor('GradeLevel', 'Tenth grade')
