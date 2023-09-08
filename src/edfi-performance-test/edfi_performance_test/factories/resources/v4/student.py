# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import factory

from edfi_performance_test.factories.resources.api_factory import APIFactory
from edfi_performance_test.api.client.student import StudentClient


class StudentGradebookEntryFactoryV4(APIFactory):
    gradebookEntryReference = factory.Dict(
        dict(
            gradebookEntryIdentifier=None,
            namespace="uri://ed-fi.org/GradebookEntry/GradebookEntry.xml",
        )
    )
    studentReference = factory.Dict(
        dict(studentUniqueId=StudentClient.shared_student_id())
    )
    numericGradeEarned = 80
