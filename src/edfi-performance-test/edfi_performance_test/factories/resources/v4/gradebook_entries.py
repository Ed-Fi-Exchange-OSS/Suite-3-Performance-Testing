# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import factory

from edfi_performance_test.api.client.school import SchoolClient
from edfi_performance_test.factories.resources.api_factory import APIFactory
from edfi_performance_test.factories.utils import (
    UniqueIdAttribute,
    formatted_date,
    current_year,
    RandomSuffixAttribute,
)


class GradebookEntryFactoryV4(APIFactory):
    gradebookEntryIdentifier = UniqueIdAttribute(num_chars=16)
    namespace = "uri://ed-fi.org/GradebookEntry/GradebookEntry.xml"
    title = RandomSuffixAttribute("Assignment", suffix_length=10)
    dateAssigned = formatted_date(2, 2)
    sectionReference = factory.Dict(
        dict(
            localCourseCode="ELA-01",
            schoolId=SchoolClient.shared_elementary_school_id(),
            schoolYear=current_year(),
            sectionIdentifier="ELA012017RM555",
            sessionName="2016-2017 Fall Semester",
        )
    )
    sourceSectionIdentifier = UniqueIdAttribute(num_chars=255)
