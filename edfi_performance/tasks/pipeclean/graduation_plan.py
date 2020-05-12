from edfi_performance.tasks.pipeclean import EdFiPipecleanTestBase


class GraduationPlanPipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = 'totalRequiredCredits'
    update_attribute_value = 30
