import factory

from edfi_performance.api.client.education import LocalEducationAgencyClient
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
        'localEducationAgencyId': LocalEducationAgencyClient.shared_education_organization_id(),
    }


class SchoolYearTypeFactory(APIFactory):
    pass  # Cannot be created, modified, or deleted because it is a core enumeration defined by the API implementer
