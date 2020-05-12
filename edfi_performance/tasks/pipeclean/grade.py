from edfi_performance.tasks.pipeclean import EdFiPipecleanTestBase


class GradePipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = 'numericGradeEarned'
    update_attribute_value = 83
