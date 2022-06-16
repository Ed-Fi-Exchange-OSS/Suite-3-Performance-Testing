# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import factory

from edfi_performance_test.api.client.school import SchoolClient
from edfi_performance_test.factories import APIFactory
from edfi_performance_test.factories.utils import UniqueIdAttribute, formatted_date

class AcademicWeekFactory(APIFactory):
    weekIdentifier = UniqueIdAttribute()
    schoolReference = factory.Dict(dict(schoolId=SchoolClient.shared_elementary_school_id()))
    beginDate = formatted_date(8, 7)
    endDate = formatted_date(8, 13)
    totalInstructionalDays = 5

from .. import APIFactory
from ..descriptors.utils import build_descriptor_dicts, ListOfDescriptors
from ..resources.address import AddressFactory
from ..utils import UniquePrimaryKeyAttribute, RandomSuffixAttribute


class SchoolFactory(APIFactory):
    schoolId = UniquePrimaryKeyAttribute()
    shortNameOfInstitution = RandomSuffixAttribute("GOHS")
    nameOfInstitution = factory.LazyAttribute(
        lambda o: "Grand Oaks High School {}".format(o.shortNameOfInstitution[-4:])
    )
    addresses = factory.List([
        factory.SubFactory(AddressFactory),
    ])
    educationOrganizationCategories = ListOfDescriptors('EducationOrganizationCategory', ['School'])
    educationOrganizationCodes = factory.LazyAttribute(
        lambda o: build_descriptor_dicts(
            'EducationOrganizationIdentificationSystem',
            [('SEA', {'identificationCode': str(o.schoolId)})]
        )
    )
    gradeLevels = ListOfDescriptors(
        'GradeLevel',
        ['Ninth grade', 'Tenth grade', 'Eleventh grade', 'Twelfth grade']
    )
    institutionTelephones = ListOfDescriptors(
        'InstitutionTelephoneNumberType',
        [('Main', {'telephoneNumber': '(950) 325-9465'})]
    )
    localEducationAgencyReference = {
        'localEducationAgencyId': '255901' #LocalEducationAgencyClient.shared_education_organization_id(),
    }


class SchoolYearTypeFactory(APIFactory):
    pass  # Cannot be created, modified, or deleted because it is a core enumeration defined by the API implementer
