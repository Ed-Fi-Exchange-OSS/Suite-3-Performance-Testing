# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import factory

from edfi_performance_test.api.client.education import LocalEducationAgencyClient
from edfi_performance_test.factories.resources.api_factory import APIFactory
from edfi_performance_test.factories.utils import UniqueIdAttribute


class AccountabilityRatingFactory(APIFactory):
    ratingTitle = UniqueIdAttribute()
    educationOrganizationReference = factory.Dict(dict(educationOrganizationId=LocalEducationAgencyClient.shared_education_organization_id()))
    schoolYearTypeReference = factory.Dict(dict(schoolYear=2014))
    rating = "Recognized"
