import factory

from edfi_performance.api.client.education import LocalEducationAgencyClient
from edfi_performance.factories import APIFactory
from edfi_performance.factories.descriptors.utils import build_descriptor
from edfi_performance.factories.utils import UniqueIdAttribute, formatted_date


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
