# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from edfi_performance_test.tasks.pipeclean.ed_fi_pipeclean_test_base import (
    EdFiPipecleanTestBase,
)
from edfi_performance_test.tasks.pipeclean.assessment import (
    AssessmentPipecleanTest,
    AssessmentItemPipecleanTest,
    LearningObjectivePipecleanTest,
    LearningStandardPipecleanTest,
    ObjectiveAssessmentPipecleanTest,
    StudentAssessmentPipecleanTest,
)


class SkipAssessmentPipecleanTest(AssessmentPipecleanTest):
    @classmethod
    def skip_all_scenarios(cls):
        return True


class SkipAssessmentItemPipecleanTest(AssessmentItemPipecleanTest):
    @classmethod
    def skip_all_scenarios(cls):
        return True


class SkipLearningObjectivePipecleanTest(LearningObjectivePipecleanTest):
    @classmethod
    def skip_all_scenarios(cls):
        return True


class SkipLearningStandardPipecleanTest(LearningStandardPipecleanTest):
    @classmethod
    def skip_all_scenarios(cls):
        return True


class SkipObjectiveAssessmentPipecleanTest(ObjectiveAssessmentPipecleanTest):
    @classmethod
    def skip_all_scenarios(cls):
        return True


class SkipStudentAssessmentPipecleanTest(StudentAssessmentPipecleanTest):
    @classmethod
    def skip_all_scenarios(cls):
        return True


# call all again now in v5

class AssessmentPipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = "title"
    update_attribute_value = "AP English 3"


class AssessmentItemPipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = "correctResponse"
    update_attribute_value = "C"


class LearningStandardPipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = "courseTitle"
    update_attribute_value = "Advanced Math for students v4.6"


class ObjectiveAssessmentPipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = "maxRawScore"
    update_attribute_value = 10


class StudentAssessmentPipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = "serialNumber"
    update_attribute_value = 2
