# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import factory

from edfi_performance_test.api.client.school import SchoolClient
from edfi_performance_test.factories.resources.api_factory import APIFactory
from edfi_performance_test.factories.descriptors.utils import build_descriptor
from edfi_performance_test.factories.utils import UniqueIdAttribute


class SessionFactory(APIFactory):
    schoolReference = factory.Dict(
        dict(schoolId=SchoolClient.shared_elementary_school_id())
    )  # Prepopulated school
    schoolYearTypeReference = factory.Dict(dict(schoolYear=2014))
    sessionName = UniqueIdAttribute()
    gradingPeriods = factory.List(
        [
            factory.Dict(
                dict(
                    gradingPeriodReference=factory.Dict(
                        dict(
                            gradingPeriodDescriptor=build_descriptor(
                                "GradingPeriod", "First Six Weeks"
                            ),
                            periodSequence=None,  # Must be entered by client
                        )
                    ),
                ),
            ),
            factory.Dict(
                dict(
                    gradingPeriodReference=factory.Dict(
                        dict(
                            gradingPeriodDescriptor=build_descriptor(
                                "GradingPeriod", "Second Six Weeks"
                            ),
                            periodSequence=None,  # Must be entered by client
                        )
                    ),
                ),
            ),
        ]
    )
    beginDate = "2014-08-23"
    endDate = "2014-12-15"
    termDescriptor = build_descriptor("Term", "Fall Semester")
    totalInstructionalDays = 88
