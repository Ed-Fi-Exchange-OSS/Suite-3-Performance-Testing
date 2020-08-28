# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import factory

from edfi_performance.api.client.education import LocalEducationAgencyClient
from .. import APIFactory
from ..descriptors.utils import build_descriptor
from ..utils import RandomSuffixAttribute


class ProgramFactory(APIFactory):
    programId = '101'
    programName = RandomSuffixAttribute("Grand Bend Bilingual 101")
    programTypeDescriptor = build_descriptor('ProgramType', 'Bilingual')
    educationOrganizationReference = factory.Dict(
        dict(educationOrganizationId=LocalEducationAgencyClient.shared_education_organization_id())
    )
