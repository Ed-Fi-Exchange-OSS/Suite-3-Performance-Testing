# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.


from edfi_performance_test.tasks.volume.student import (
    StudentParentAssociationVolumeTest,
    StudentDisciplineIncidentAssociationVolumeTest,
)


class SkipStudentParentAssociationVolumeTest(StudentParentAssociationVolumeTest):
    @classmethod
    def skip_all_scenarios(cls):
        return True


class SkipStudentDisciplineIncidentAssociationVolumeTest(StudentDisciplineIncidentAssociationVolumeTest):
    @classmethod
    def skip_all_scenarios(cls):
        return True
