from edfi_performance.tasks.pipeclean import EdFiPipecleanTestBase


class AccountabilityRatingPipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = 'rating'
    update_attribute_value = "Exemplary"
