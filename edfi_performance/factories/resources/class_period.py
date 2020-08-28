# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import factory

from edfi_performance.api.client.school import SchoolClient
from .. import APIFactory
from ..utils import RandomSuffixAttribute


class ClassPeriodFactory(APIFactory):
    classPeriodName = RandomSuffixAttribute("Class Period 1", suffix_length=10)
    schoolReference = factory.Dict(dict(schoolId=SchoolClient.shared_elementary_school_id()))  # Prepopulated school
    officialAttendancePeriod = False
