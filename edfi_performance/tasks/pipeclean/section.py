from edfi_performance.factories.utils import formatted_date
from edfi_performance.tasks.pipeclean import EdFiPipecleanTestBase


class SectionPipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = 'availableCredits'
    update_attribute_value = 2


class SectionAttendanceTakenEventPipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = 'eventDate'
    update_attribute_value = formatted_date(8, 8)
