from edfi_performance.tasks.pipeclean import EdFiPipecleanTestBase


class CourseOfferingPipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = 'localCourseTitle'
    update_attribute_value = "English Language Arts, Grade 1"
