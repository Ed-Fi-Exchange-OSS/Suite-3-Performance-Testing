# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import factory

from edfi_performance.api.client.school import SchoolClient
from edfi_performance.factories.utils import current_year
from .. import APIFactory
from ..descriptors.utils import build_descriptor_dicts


class CalendarDateFactory(APIFactory):
    calendarReference = factory.Dict(
        dict(
            calendarCode="107SS111111",
            schoolId=SchoolClient.shared_elementary_school_id(),
            schoolYear=current_year(),
        )
    )
    calendarEvents = build_descriptor_dicts('CalendarEvent', ['Holiday'])
    date = "2014-09-16"
