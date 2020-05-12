from edfi_performance.factories.descriptors.utils import build_descriptor
from edfi_performance.tasks.pipeclean import EdFiPipecleanTestBase


class DisciplineIncidentPipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = 'reporterName'
    update_attribute_value = "Villa, Mark"


class DisciplineActionPipecleanTest(EdFiPipecleanTestBase):
    def _touch_put_endpoint(self, resource_id, attrs):
        attrs['disciplines'][0]['disciplineDescriptor'] = build_descriptor('Discipline', 'In School Suspension')
        self.update(resource_id, **attrs)
