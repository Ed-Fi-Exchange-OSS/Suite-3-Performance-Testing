# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import factory

from edfi_performance_test.api.client.student import StudentClient
from edfi_performance_test.factories.resources.api_factory import APIFactory
from edfi_performance_test.factories.descriptors.utils import ListOfDescriptors, build_descriptor
from edfi_performance_test.factories.resources.address import AddressFactory
from edfi_performance_test.factories.utils import UniquePrimaryKeyAttribute, RandomDateAttribute


class PostSecondaryInstitutionFactory(APIFactory):
    postSecondaryInstitutionId = UniquePrimaryKeyAttribute()
    nameOfInstitution = "University of Texas at Austin"
    addresses = factory.List([
        factory.SubFactory(AddressFactory),
    ])
    categories = ListOfDescriptors('EducationOrganizationCategory', ['Post Secondary Institution'])


class PostSecondaryEventFactory(APIFactory):
    eventDate = RandomDateAttribute()
    studentReference = factory.Dict(dict(studentUniqueId=StudentClient.shared_student_id()))
    postSecondaryEventCategoryDescriptor = build_descriptor('PostSecondaryEventCategory', 'College Acceptance')
    postSecondaryInstitutionReference = factory.Dict(dict(postSecondaryInstitutionId=None))  # Must be entered by user
