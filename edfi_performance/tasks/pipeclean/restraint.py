from edfi_performance.factories.utils import formatted_date
from edfi_performance.tasks.pipeclean import EdFiPipecleanTestBase


class RestraintEventPipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = 'eventDate'
    update_attribute_value = formatted_date(2, 15)
