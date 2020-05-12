from edfi_performance.tasks.pipeclean import EdFiPipecleanTestBase


class SessionPipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = 'endDate'
    update_attribute_value = "2014-12-16"
