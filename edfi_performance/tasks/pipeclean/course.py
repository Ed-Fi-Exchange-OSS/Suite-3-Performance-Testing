from edfi_performance.tasks.pipeclean import EdFiPipecleanTestBase


class CoursePipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = 'courseTitle'
    update_attribute_value = "Algebra II"


class CourseTranscriptPipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = 'finalNumericGradeEarned'
    update_attribute_value = 87
