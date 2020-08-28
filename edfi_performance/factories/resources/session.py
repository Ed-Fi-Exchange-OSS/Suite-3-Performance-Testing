# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import factory

from edfi_performance.api.client.school import SchoolClient
from .. import APIFactory
from ..descriptors.utils import build_descriptor
from ..utils import RandomSuffixAttribute


class SessionFactory(APIFactory):
    schoolReference = factory.Dict(dict(schoolId=SchoolClient.shared_elementary_school_id()))  # Prepopulated school
    schoolYearTypeReference = factory.Dict(dict(schoolYear=2014))
    sessionName = RandomSuffixAttribute("2016-2017 Fall Semester")
    gradingPeriods = factory.List([
        factory.Dict(
            dict(
                gradingPeriodReference=factory.Dict(dict(
                    gradingPeriodDescriptor=build_descriptor("GradingPeriod", "First Six Weeks"),
                    periodSequence=None  # Must be entered by client
                )),
            ),
        ),
        factory.Dict(
            dict(
                gradingPeriodReference=factory.Dict(dict(
                    gradingPeriodDescriptor=build_descriptor("GradingPeriod", "Second Six Weeks"),
                    periodSequence=None  # Must be entered by client
                )),
            ),
        )
    ])
    beginDate = "2014-08-23"
    endDate = "2014-12-15"
    termDescriptor = build_descriptor('Term', 'Fall Semester')
    totalInstructionalDays = 88
