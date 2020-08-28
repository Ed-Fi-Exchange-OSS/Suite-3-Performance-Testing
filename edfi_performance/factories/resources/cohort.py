# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import factory

from edfi_performance.api.client.school import SchoolClient
from .. import APIFactory
from ..descriptors.utils import build_descriptor
from ..utils import RandomSuffixAttribute


class CohortFactory(APIFactory):
    cohortIdentifier = RandomSuffixAttribute("1")
    educationOrganizationReference = factory.Dict({
                                         "educationOrganizationId": SchoolClient.shared_elementary_school_id()
                                     })
    cohortDescription = "Cohort 1 Description"
    cohortScopeDescriptor = build_descriptor("CohortScope", "District")
    cohortTypeDescriptor = build_descriptor("CohortType", "Study Hall")
