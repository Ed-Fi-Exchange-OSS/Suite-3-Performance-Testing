from edfi_performance.factories.descriptors.utils import build_descriptor
from edfi_performance.tasks.pipeclean import EdFiPipecleanTestBase


class CalendarPipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = 'calendarTypeDescriptor'
    update_attribute_value = build_descriptor('CalendarType', 'Student Specific')
