# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import factory

from edfi_performance_test.factories.resources.api_factory import APIFactory
from edfi_performance_test.factories.descriptors.utils import (
    build_descriptor,
    build_descriptor_dicts,
    ListOfDescriptors,
)
from edfi_performance_test.factories.resources.address import AddressFactory
from edfi_performance_test.factories.utils import (
    UniqueIdAttribute,
    formatted_date,
    UniquePrimaryKeyAttribute,
)


class CommunityOrganizationFactory(APIFactory):
    communityOrganizationId = UniquePrimaryKeyAttribute()
    nameOfInstitution = "Foundation for the Arts"
    addresses = factory.List(
        [
            factory.SubFactory(AddressFactory),
        ]
    )
    categories = ListOfDescriptors("EducationOrganizationCategory", ["School"])
    educationOrganizationCodes = factory.LazyAttribute(
        lambda o: build_descriptor_dicts(
            "EducationOrganizationIdentificationSystem",
            [("Other", {"identificationCode": o.communityOrganizationId})],
        )
    )


class CommunityProviderFactory(APIFactory):
    communityProviderId = UniquePrimaryKeyAttribute()
    communityOrganizationReference = factory.Dict(
        dict(communityOrganizationId=None)
    )  # Need to create as dependency
    nameOfInstitution = "Provider for the Arts"
    providerProfitabilityDescriptor = build_descriptor(
        "ProviderProfitability", "Nonprofit"
    )
    providerStatusDescriptor = build_descriptor("ProviderStatus", "Active")
    providerCategoryDescriptor = build_descriptor("ProviderCategory", "Center-EC")
    addresses = factory.List(
        [
            factory.SubFactory(AddressFactory),
        ]
    )
    categories = ListOfDescriptors("EducationOrganizationCategory", ["School"])
    educationOrganizationCodes = factory.LazyAttribute(
        lambda o: build_descriptor_dicts(
            "EducationOrganizationIdentificationSystem",
            [("Other", {"identificationCode": o.communityProviderId})],
        )
    )


class CommunityProviderLicenseFactory(APIFactory):
    licenseIdentifier = UniqueIdAttribute(num_chars=20)
    communityProviderReference = factory.Dict(
        dict(communityProviderId=None)
    )  # Need to create as dependency
    licensingOrganization = "USDOE"
    licenseTypeDescriptor = build_descriptor("LicenseType", "School Age Program")
    licenseEffectiveDate = formatted_date(11, 24)
