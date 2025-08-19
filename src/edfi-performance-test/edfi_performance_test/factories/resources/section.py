# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import factory

from edfi_performance_test.api.client.school import SchoolClient
from edfi_performance_test.factories.resources.api_factory import APIFactory
from edfi_performance_test.factories.descriptors.utils import build_descriptor
from edfi_performance_test.factories.utils import RandomSuffixAttribute, formatted_date


class SectionFactory(APIFactory):
    educationalEnvironmentDescriptor = build_descriptor(
        "EducationalEnvironment", "Classroom"
    )
    sectionIdentifier = RandomSuffixAttribute("ELA012017RM555")
    availableCredits = 1
    sequenceOfCourse = 1
    classPeriods = factory.List(
        [
            factory.Dict(
                dict(
                    classPeriodReference=factory.Dict(
                        dict(classPeriodName=None, schoolId=SchoolClient.shared_elementary_school_id()),  # Must be entered by client
                    ),
                ),
            ),
        ]
    )
    courseOfferingReference = factory.Dict(
        dict(
            localCourseCode="ELA-01",  # Will need to override this with reference value
            schoolId=SchoolClient.shared_elementary_school_id(),
            schoolYear=2014,
            sessionName="2016-2017 Fall Semester",  # Will need to override this with reference value
        )
    )
    locationReference = factory.Dict(
        dict(
            schoolId=SchoolClient.shared_elementary_school_id(),
            classroomIdentificationCode="501",  # Will need to override this with reference value
        )
    )


class SectionAttendanceTakenEventFactory(APIFactory):
    calendarDateReference = factory.Dict(
        dict(
            calendarCode="107SS111111",
            schoolId=SchoolClient.shared_elementary_school_id(),
            schoolYear=2014,
            date=formatted_date(9, 16, 2014),
        )
    )
    sectionReference = factory.Dict(
        dict(
            sectionIdentifier=None,  # Must be created
            localCourseCode="ELA-01",
            schoolId=SchoolClient.shared_elementary_school_id(),
            schoolYear=2014,
            sessionName="2016-2017 Fall Semester",
        )
    )
    eventDate = formatted_date(9, 9)
