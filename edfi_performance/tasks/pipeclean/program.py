from edfi_performance.factories.descriptors.utils import build_descriptor
from edfi_performance.tasks.pipeclean import EdFiPipecleanTestBase


class ProgramPipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = 'programTypeDescriptor'
    update_attribute_value = build_descriptor('ProgramType', 'Special Education')
