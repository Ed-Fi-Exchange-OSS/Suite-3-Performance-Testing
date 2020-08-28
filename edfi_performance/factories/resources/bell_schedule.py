# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import factory

from edfi_performance.api.client.school import SchoolClient
from edfi_performance.factories import APIFactory
from edfi_performance.factories.utils import UniqueIdAttribute


class BellScheduleFactory(APIFactory):
    bellScheduleName = UniqueIdAttribute()
    schoolReference = factory.Dict(dict(schoolId=SchoolClient.shared_elementary_school_id()))
    classPeriods = factory.List([
        factory.Dict(
            dict(
                classPeriodReference=factory.Dict(dict(classPeriodName=None)),
            )
        ),
    ])
    alternateDayName = "Red"
