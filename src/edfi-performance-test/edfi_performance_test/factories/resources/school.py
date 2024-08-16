# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import factory

from edfi_performance_test.factories.descriptors.utils import (
    build_descriptor_dicts,
    ListOfDescriptors,
)
from edfi_performance_test.factories.resources.address import AddressFactory
from edfi_performance_test.factories.resources.api_factory import APIFactory
from edfi_performance_test.factories.utils import (
    RandomSuffixAttribute,
    UniquePrimaryKeyAttribute,
)
from edfi_performance_test.helpers.config import get_config_value


class SchoolFactory(APIFactory):
    schoolId = UniquePrimaryKeyAttribute()
    shortNameOfInstitution = RandomSuffixAttribute("GOHS")
    nameOfInstitution = factory.LazyAttribute(
        lambda o: "Grand Oaks High School {}".format(o.shortNameOfInstitution[-4:])
    )
    addresses = factory.List(
        [
            factory.SubFactory(AddressFactory),
        ]
    )
    educationOrganizationCategories = ListOfDescriptors(
        "EducationOrganizationCategory", ["School"]
    )
    identificationCodes = factory.LazyAttribute(
        lambda o: build_descriptor_dicts(
            "EducationOrganizationIdentificationSystem",
            [("SEA", {"identificationCode": str(o.schoolId)})],
        )
    )
    gradeLevels = ListOfDescriptors(
        "GradeLevel", ["Ninth grade", "Tenth grade", "Eleventh grade", "Twelfth grade"]
    )
    institutionTelephones = ListOfDescriptors(
        "InstitutionTelephoneNumberType",
        [("Main", {"telephoneNumber": "(950) 325-9465"})],
    )
    localEducationAgencyReference = {
        "localEducationAgencyId": get_config_value("PERF_LOCAL_EDUCATION_ORGANIZATION_ID", "255901")
    }


class SchoolYearTypeFactory(APIFactory):
    pass  # Cannot be created, modified, or deleted because it is a core enumeration defined by the API implementer
