from edfi_performance.factories.descriptors.utils import build_descriptor
from edfi_performance.tasks.pipeclean import EdFiPipecleanTestBase


class CohortPipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = 'cohortTypeDescriptor'
    update_attribute_value = build_descriptor("CohortType", "Field Trip")
