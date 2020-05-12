import factory

from .. import APIFactory
from ..descriptors.utils import build_descriptor


class GraduationPlanFactory(APIFactory):
    totalRequiredCredits = 28
    graduationPlanTypeDescriptor = build_descriptor('GraduationPlanType', 'Recommended')
    educationOrganizationReference = factory.Dict(
        dict(educationOrganizationId=None),
    )
    graduationSchoolYearTypeReference = factory.Dict(
        dict(schoolYear=2014),
    )
