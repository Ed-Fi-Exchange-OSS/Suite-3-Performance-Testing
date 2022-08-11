# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import factory

from edfi_performance_test.api.client.school import SchoolClient
from edfi_performance_test.factories.utils import (
    RandomSchoolYearAttribute,
    RandomDateAttribute,
)
from edfi_performance_test.factories.resources.api_factory import APIFactory
from edfi_performance_test.factories.descriptors.utils import build_descriptor_dicts


class CalendarDateFactory(APIFactory):
    calendarReference = factory.Dict(
        dict(
            calendarCode="107SS111111",
            schoolId=SchoolClient.shared_elementary_school_id(),
            schoolYear=RandomSchoolYearAttribute(),
        )
    )
    calendarEvents = build_descriptor_dicts("CalendarEvent", ["Holiday"])
    date = RandomDateAttribute()
