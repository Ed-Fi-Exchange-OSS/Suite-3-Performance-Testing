from edfi_performance.factories.descriptors.utils import build_descriptor_dicts
from edfi_performance.tasks.pipeclean import EdFiPipecleanTestBase


class CalendarDatePipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = 'calendarEvents'
    update_attribute_value = build_descriptor_dicts(
        'CalendarEvent',
        ['Instructional day', 'Student late arrival/early dismissal'])
