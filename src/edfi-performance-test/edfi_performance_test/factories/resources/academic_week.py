# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import factory

from edfi_performance_test.factories.resources.api_factory import APIFactory
from edfi_performance_test.factories.utils import UniqueIdAttribute, formatted_date


class AcademicWeekFactory(APIFactory):
    weekIdentifier = UniqueIdAttribute()
    schoolReference = factory.Dict(dict(schoolId=None))
    beginDate = formatted_date(8, 7)
    endDate = formatted_date(8, 13)
    totalInstructionalDays = 5
