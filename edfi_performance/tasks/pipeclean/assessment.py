from edfi_performance.tasks.pipeclean import EdFiPipecleanTestBase


class AssessmentPipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = 'title'
    update_attribute_value = "AP English 3"


class AssessmentItemPipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = 'correctResponse'
    update_attribute_value = 'C'


class LearningObjectivePipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = 'description'
    update_attribute_value = (
        "The student will demonstrate the ability to utilize numbers to perform"
        " operations with complex concepts at a high level."
    )


class LearningStandardPipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = 'courseTitle'
    update_attribute_value = "Advanced Math for students v4.6"


class ObjectiveAssessmentPipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = 'maxRawScore'
    update_attribute_value = 10


class StudentAssessmentPipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = 'serialNumber'
    update_attribute_value = 2
