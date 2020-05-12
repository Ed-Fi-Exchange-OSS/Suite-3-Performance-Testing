from edfi_performance.tasks.pipeclean import EdFiPipecleanTestBase


class AcademicWeekPipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = 'totalInstructionalDays'
    update_attribute_value = 4
