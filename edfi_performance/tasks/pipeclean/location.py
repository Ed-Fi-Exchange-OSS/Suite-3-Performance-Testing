from edfi_performance.tasks.pipeclean import EdFiPipecleanTestBase


class LocationPipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = 'maximumNumberOfSeats'
    update_attribute_value = 20
