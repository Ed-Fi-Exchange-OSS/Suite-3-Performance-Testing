from edfi_performance.factories.utils import formatted_date
from edfi_performance.tasks.pipeclean import EdFiPipecleanTestBase


class GradebookEntryPipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = 'dateAssigned'
    update_attribute_value = formatted_date(3, 3)
