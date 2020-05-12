import factory

from edfi_performance.api.client.education import LocalEducationAgencyClient
from .. import APIFactory
from ..descriptors.utils import build_descriptor
from ..utils import RandomSuffixAttribute


class ProgramFactory(APIFactory):
    programId = '101'
    programName = RandomSuffixAttribute("Grand Bend Bilingual 101")
    programTypeDescriptor = build_descriptor('ProgramType', 'Bilingual')
    educationOrganizationReference = factory.Dict(
        dict(educationOrganizationId=LocalEducationAgencyClient.shared_education_organization_id())
    )
