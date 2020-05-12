from edfi_performance.factories.utils import RandomSuffixAttribute
from edfi_performance.tasks.pipeclean import EdFiPipecleanTestBase


class ClassPeriodPipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = 'classPeriodName'
    update_attribute_value = RandomSuffixAttribute("Class Period 01", suffix_length=10)
