from edfi_performance.tasks.pipeclean import EdFiPipecleanTestBase


class BellSchedulePipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = 'alternateDayName'
    update_attribute_value = "Blue"
