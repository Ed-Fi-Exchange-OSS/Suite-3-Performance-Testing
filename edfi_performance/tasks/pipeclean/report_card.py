from edfi_performance.tasks.pipeclean import EdFiPipecleanTestBase


class ReportCardPipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = 'gpaGivenGradingPeriod'
    update_attribute_value = 2.78
