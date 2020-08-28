# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import factory

from edfi_performance.api.client.school import SchoolClient
from edfi_performance.api.client.student import StudentClient
from edfi_performance.factories import APIFactory
from edfi_performance.factories.utils import UniqueIdAttribute, formatted_date


class RestraintEventFactory(APIFactory):
    restraintEventIdentifier = UniqueIdAttribute(num_chars=20)
    schoolReference = factory.Dict(dict(schoolId=SchoolClient.shared_elementary_school_id()))
    studentReference = factory.Dict(dict(studentUniqueId=StudentClient.shared_student_id()))
    eventDate = formatted_date(2, 14)
