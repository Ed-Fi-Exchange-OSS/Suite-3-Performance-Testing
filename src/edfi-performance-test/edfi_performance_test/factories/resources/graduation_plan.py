# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import factory

from edfi_performance_test.factories.resources.api_factory import APIFactory
from edfi_performance_test.factories.descriptors.utils import build_descriptor
from edfi_performance_test.factories.utils import RandomSchoolYearAttribute


class GraduationPlanFactory(APIFactory):
    totalRequiredCredits = 28
    graduationPlanTypeDescriptor = build_descriptor("GraduationPlanType", "Recommended")
    educationOrganizationReference = factory.Dict(
        dict(educationOrganizationId=None),
    )
    graduationSchoolYearTypeReference = factory.Dict(
        dict(schoolYear=RandomSchoolYearAttribute())
    )
