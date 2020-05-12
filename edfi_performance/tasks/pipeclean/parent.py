from edfi_performance.factories.descriptors.utils import build_descriptor
from edfi_performance.tasks.pipeclean import EdFiPipecleanTestBase


class ParentPipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = 'parentOtherNames'
    update_attribute_value = [
        {
            'firstName': "Lexi",
            'lastSurname': "Johnson",
            'otherNameTypeDescriptor': build_descriptor('OtherNameType', 'Nickname'),
        }
    ]
