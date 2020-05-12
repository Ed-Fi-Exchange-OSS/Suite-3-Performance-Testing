from edfi_performance.factories.utils import formatted_date
from edfi_performance.tasks.pipeclean import EdFiPipecleanTestBase


class CredentialPipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = 'issuanceDate'
    update_attribute_value = formatted_date(8, 4)
