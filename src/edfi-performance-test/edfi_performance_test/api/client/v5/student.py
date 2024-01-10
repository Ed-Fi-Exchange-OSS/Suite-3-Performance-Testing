# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from typing import Dict

from edfi_performance_test.api.client.ed_fi_api_client import EdFiAPIClient
from edfi_performance_test.api.client.v5.contact import ContactClient
from edfi_performance_test.api.client.school import SchoolClient
from edfi_performance_test.api.client.student import StudentClient
from edfi_performance_test.api.client.program import ProgramClient
from edfi_performance_test.factories.descriptors.utils import (
    build_descriptor,
)


class StudentContactAssociationClient(EdFiAPIClient):
    endpoint = "studentContactAssociations"

    def create_with_dependencies(self, **kwargs):
        # Prepopulated student
        studentUniqueId = kwargs.pop("studentUniqueId", StudentClient.shared_student_id())

        # Create contact
        contact_unique_id = kwargs.pop("contactUniqueId", ContactClient.shared_contact_id())

        # Create contact - student association
        return self.create_using_dependencies(
            contactReference__contactUniqueId=contact_unique_id,
            studentReference__studentUniqueId=studentUniqueId,
            **kwargs
        )


class StudentProgramEvaluationClient(EdFiAPIClient):
    endpoint = "studentProgramEvaluations"

    dependencies: Dict = {
        "edfi_performance_test.api.client.v5.program.ProgramEvaluationClient": {},
    }

    def create_with_dependencies(self, **kwargs):
        # Prepopulated student
        studentUniqueId = kwargs.pop("studentUniqueId", StudentClient.shared_student_id())

        prog_eval_ref = self.program_evaluation_client.create_with_dependencies()

        return self.create_using_dependencies(
            prog_eval_ref,
            programEvaluationReference__programEducationOrganizationId=prog_eval_ref[
                "attributes"]["programReference"]["educationOrganizationId"],
            programEvaluationReference__programEvaluationPeriodDescriptor=prog_eval_ref[
                "attributes"]["programEvaluationPeriodDescriptor"],
            programEvaluationReference__programEvaluationTitle=prog_eval_ref[
                "attributes"]["programEvaluationTitle"],
            programEvaluationReference__programEvaluationTypeDescriptor=prog_eval_ref[
                "attributes"]["programEvaluationTypeDescriptor"],
            programEvaluationReference__programName=prog_eval_ref[
                "attributes"]["programReference"]["programName"],
            programEvaluationReference__programTypeDescriptor=prog_eval_ref[
                "attributes"]["programReference"]["programTypeDescriptor"],
            studentReference__studentUniqueId=studentUniqueId,
            **kwargs
        )


class StudentSpecialEducationProgramEligibilityAssociationClient(EdFiAPIClient):
    endpoint = "studentSpecialEducationProgramEligibilityAssociations"

    dependencies: Dict = {StudentClient: {}}

    def create_with_dependencies(self, **kwargs):
        school_id = kwargs.pop("schoolId", SchoolClient.shared_elementary_school_id())
        program = ProgramClient.shared_program_name()

        # Create enrolled student
        student_reference = self.student_client.create_with_dependencies(
            schoolId=school_id
        )

        # Create student program association
        return self.create_using_dependencies(
            student_reference,
            studentReference__studentUniqueId=student_reference["attributes"][
                "studentUniqueId"
            ],
            programReference__programName=program,
            programReference__programTypeDescriptor=build_descriptor(
                "ProgramType", program
            ),
            **kwargs
        )
