import factory

from edfi_performance.api.client.education import LocalEducationAgencyClient
from edfi_performance.factories import APIFactory
from edfi_performance.factories.utils import UniqueIdAttribute


class AccountabilityRatingFactory(APIFactory):
    ratingTitle = UniqueIdAttribute()
    educationOrganizationReference = factory.Dict(dict(educationOrganizationId=LocalEducationAgencyClient.shared_education_organization_id()))
    schoolYearTypeReference = factory.Dict(dict(schoolYear=2014))
    rating = "Recognized"
