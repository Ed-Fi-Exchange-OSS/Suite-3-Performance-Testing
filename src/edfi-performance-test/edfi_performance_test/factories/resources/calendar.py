﻿# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import factory

from edfi_performance_test.api.client.school import SchoolClient
from edfi_performance_test.factories.resources.api_factory import APIFactory
from edfi_performance_test.factories.descriptors.utils import build_descriptor
from edfi_performance_test.factories.utils import RandomSuffixAttribute


class CalendarFactory(APIFactory):
    schoolYearTypeReference = factory.Dict({
        'schoolYear': 2014,
    })
    calendarTypeDescriptor = build_descriptor("CalendarType", "IEP")
    calendarCode = RandomSuffixAttribute("107SS111111")
    schoolReference = factory.Dict({
        "schoolId": SchoolClient.shared_elementary_school_id()
    })
