from edfi_performance.tasks.pipeclean import EdFiPipecleanTestBase


class CompetencyObjectivePipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = 'objectiveGradeLevelDescriptor'
    update_attribute_value = "Twelfth grade"
