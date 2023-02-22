# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import factory

from edfi_performance_test.api.client.education import LocalEducationAgencyClient
from edfi_performance_test.factories.resources.api_factory import APIFactory
from edfi_performance_test.factories.descriptors.utils import (
    build_descriptor,
    ListOfDescriptors,
    build_descriptor_dicts,
)
from edfi_performance_test.factories.resources.address import AddressFactory
from edfi_performance_test.factories.utils import (
    UniqueIdAttribute,
    UniquePrimaryKeyAttribute,
    formatted_date,
)


class EducationServiceCenterFactory(APIFactory):
    educationServiceCenterId = UniquePrimaryKeyAttribute()
    nameOfInstitution = "Texas DoE Service Center"
    addresses = factory.List(
        [
            factory.SubFactory(AddressFactory),
        ]
    )
    categories = ListOfDescriptors(
        "EducationOrganizationCategory", ["Education Service Center"]
    )
    identificationCodes = factory.LazyAttribute(
        lambda o: build_descriptor_dicts(
            "EducationOrganizationIdentificationSystem",
            [("SEA", {"identificationCode": o.educationServiceCenterId})],
        )
    )


class LocalEducationAgencyFactory(APIFactory):
    localEducationAgencyId = UniquePrimaryKeyAttribute()
    nameOfInstitution = "Texas Local Education Agency"
    addresses = factory.List(
        [
            factory.SubFactory(AddressFactory),
        ]
    )
    categories = ListOfDescriptors(
        "EducationOrganizationCategory", ["Local Education Agency"]
    )
    localEducationAgencyCategoryDescriptor = build_descriptor(
        "LocalEducationAgencyCategory", "Independent"
    )
    identificationCodes = factory.LazyAttribute(
        lambda o: build_descriptor_dicts(
            "EducationOrganizationIdentificationSystem",
            [("SEA", {"identificationCode": o.localEducationAgencyId})],
        )
    )
    educationServiceCenterReference = factory.Dict(
        dict(educationServiceCenterId=None)
    )  # Must be created


class EducationContentFactory(APIFactory):
    contentIdentifier = UniqueIdAttribute(num_chars=60)
    description = "A learning resource for all grade levels"
    namespace = "uri://ed-fi.org"


class EducationOrganizationInterventionPrescriptionAssociationFactory(APIFactory):
    educationOrganizationReference = factory.Dict(
        dict(
            educationOrganizationId=LocalEducationAgencyClient.shared_education_organization_id()
        )
    )
    interventionPrescriptionReference = factory.Dict(
        dict(
            educationOrganizationId=LocalEducationAgencyClient.shared_education_organization_id(),
            interventionPrescriptionIdentificationCode=None,  # Must be created
        )
    )
    beginDate = formatted_date(4, 15)


class EducationOrganizationNetworkFactory(APIFactory):
    educationOrganizationNetworkId = UniquePrimaryKeyAttribute()
    nameOfInstitution = "Schools United Texas"
    networkPurposeDescriptor = build_descriptor("NetworkPurpose", "Shared Services")
    addresses = factory.List(
        [
            factory.SubFactory(AddressFactory),
        ]
    )
    categories = ListOfDescriptors("EducationOrganizationCategory", ["School"])
    identificationCodes = factory.LazyAttribute(
        lambda o: build_descriptor_dicts(
            "EducationOrganizationIdentificationSystem",
            [("SEA", {"identificationCode": o.educationOrganizationNetworkId})],
        )
    )


class EducationOrganizationNetworkAssociationFactory(APIFactory):
    educationOrganizationNetworkReference = factory.Dict(
        dict(educationOrganizationNetworkId=None)
    )  # Must be created
    memberEducationOrganizationReference = factory.Dict(
        dict(
            educationOrganizationId=LocalEducationAgencyClient.shared_education_organization_id()
        )
    )
    beginDate = formatted_date(1, 1)
    endDate = formatted_date(12, 31)


class EducationOrganizationPeerAssociationFactory(APIFactory):
    educationOrganizationReference = factory.Dict(
        dict(educationOrganizationId=None)
    )  # Must be created
    peerEducationOrganizationReference = factory.Dict(
        dict(educationOrganizationId=None)
    )  # Must be created


class FeederSchoolAssociationFactory(APIFactory):
    feederSchoolReference = factory.Dict(dict(schoolId=None))  # Must be created
    schoolReference = factory.Dict(dict(schoolId=None))  # Must be created
    beginDate = formatted_date(5, 29)


class StateEducationAgencyFactory(APIFactory):
    stateEducationAgencyId = UniquePrimaryKeyAttribute()
    nameOfInstitution = "Texas State Education Agency"
    addresses = factory.List(
        [
            factory.SubFactory(AddressFactory),
        ]
    )
    categories = ListOfDescriptors(
        "EducationOrganizationCategory", ["Local Education Agency"]
    )
    identificationCodes = factory.LazyAttribute(
        lambda o: build_descriptor_dicts(
            "EducationOrganizationIdentificationSystem",
            [("SEA", {"identificationCode": o.stateEducationAgencyId})],
        )
    )
