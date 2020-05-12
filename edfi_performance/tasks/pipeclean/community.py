from edfi_performance.factories.descriptors.utils import build_descriptor
from edfi_performance.factories.utils import formatted_date
from edfi_performance.tasks.pipeclean import EdFiPipecleanTestBase


class CommunityOrganizationPipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = 'nameOfInstitution'
    update_attribute_value = "Foundation for the Arts & Sciences"


class CommunityProviderPipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = 'providerStatusDescriptor'
    update_attribute_value = build_descriptor('ProviderStatus', 'Inactive')


class CommunityProviderLicensePipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = 'licenseEffectiveDate'
    update_attribute_value = formatted_date(12, 24)
