from edfi_performance.factories.descriptors.utils import build_descriptor
from edfi_performance.tasks.pipeclean import EdFiPipecleanTestBase


class PostSecondaryInstitutionPipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = 'nameOfInstitution'
    update_attribute_value = "University of Texas - Austin"


class PostSecondaryEventPipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = 'postSecondaryEventCategoryDescriptor'
    update_attribute_value = build_descriptor('PostSecondaryEventCategory', 'College Degree Received')
