from edfi_performance.tasks.pipeclean import EdFiPipecleanTestBase


class GradingPeriodPipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = 'endDate'
    update_attribute_value = '2014-10-05'
