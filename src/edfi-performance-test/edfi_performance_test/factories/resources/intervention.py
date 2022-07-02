# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import factory

from edfi_performance_test.api.client.education import LocalEducationAgencyClient
from edfi_performance_test.factories.resources.api_factory import APIFactory
from edfi_performance_test.factories.descriptors.utils import build_descriptor
from edfi_performance_test.factories.utils import UniqueIdAttribute, formatted_date


class InterventionPrescriptionFactory(APIFactory):
    interventionPrescriptionIdentificationCode = UniqueIdAttribute(num_chars=60)
    educationOrganizationReference = factory.Dict(dict(educationOrganizationId=LocalEducationAgencyClient.shared_education_organization_id()))
    deliveryMethodDescriptor = build_descriptor('DeliveryMethod', 'Whole Class')
    interventionClassDescriptor = build_descriptor('InterventionClass', 'Practice')


class InterventionFactory(APIFactory):
    interventionIdentificationCode = UniqueIdAttribute(num_chars=60)
    educationOrganizationReference = factory.Dict(dict(educationOrganizationId=LocalEducationAgencyClient.shared_education_organization_id()))
    interventionPrescriptions = factory.List([
        factory.Dict(
            dict(
                interventionPrescriptionReference=factory.Dict(
                    dict(
                        interventionPrescriptionIdentificationCode=None,  # Must be created by client
                        educationOrganizationId=LocalEducationAgencyClient.shared_education_organization_id(),
                    ),
                ),
            )
        ),
    ])
    deliveryMethodDescriptor = build_descriptor('DeliveryMethod', 'Whole Class')
    interventionClassDescriptor = build_descriptor('InterventionClass', 'Practice')
    appropriateGradeLevels = factory.List([
        factory.Dict(
            dict(gradeLevelDescriptor=build_descriptor('GradeLevel', 'Ninth grade'))
        )
    ])
    beginDate = formatted_date(8, 23)


class InterventionStudyFactory(APIFactory):
    interventionStudyIdentificationCode = UniqueIdAttribute(num_chars=60)
    educationOrganizationReference = factory.Dict(dict(educationOrganizationId=LocalEducationAgencyClient.shared_education_organization_id()))
    interventionPrescriptionReference = factory.Dict(
        dict(
            educationOrganizationId=LocalEducationAgencyClient.shared_education_organization_id(),
            interventionPrescriptionIdentificationCode=None,  # Must be created by client
        )
    )
    deliveryMethodDescriptor = build_descriptor('DeliveryMethod', 'Whole Class')
    interventionClassDescriptor = build_descriptor('InterventionClass', 'Practice')
    participants = 25
