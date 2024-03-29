# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.


from edfi_performance_test.tasks.pipeclean.student import (
    StudentParentAssociationPipecleanTest,
    StudentDisciplineIncidentAssociationPipecleanTest,
    StudentLearningObjectivePipecleanTest,
)
from edfi_performance_test.tasks.pipeclean.ed_fi_pipeclean_test_base import (
    EdFiPipecleanTestBase,
)


class SkipStudentParentAssociationPipecleanTest(StudentParentAssociationPipecleanTest):
    @classmethod
    def skip_all_scenarios(cls):
        return True


class SkipStudentDisciplineIncidentAssociationPipecleanTest(StudentDisciplineIncidentAssociationPipecleanTest):
    @classmethod
    def skip_all_scenarios(cls):
        return True


class SkipStudentLearningObjectivePipecleanTest(StudentLearningObjectivePipecleanTest):
    @classmethod
    def skip_all_scenarios(cls):
        return True


class StudentProgramEvaluationPipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = "evaluationDuration"
    update_attribute_value = 45


class StudentSpecialEducationProgramEligibilityAssociationPipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = "evaluationCompleteIndicator"
    update_attribute_value = True
