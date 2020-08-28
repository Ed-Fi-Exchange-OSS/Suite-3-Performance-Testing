﻿# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from edfi_performance.factories.descriptors.utils import build_descriptor_dicts
from edfi_performance.tasks.pipeclean import EdFiPipecleanTestBase


class CalendarDatePipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = 'calendarEvents'
    update_attribute_value = build_descriptor_dicts(
        'CalendarEvent',
        ['Instructional day', 'Student late arrival/early dismissal'])
