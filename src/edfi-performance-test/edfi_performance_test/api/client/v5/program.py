# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from typing import Dict

from edfi_performance_test.api.client.ed_fi_api_client import EdFiAPIClient


class ProgramEvaluationClient(EdFiAPIClient):
    endpoint = "programEvaluations"


class ProgramEvaluationElementClient(EdFiAPIClient):
    endpoint = "programEvaluationElements"

    dependencies: Dict = {
        "edfi_performance_test.api.client.v5.program.ProgramEvaluationClient": {}
    }

    def create_with_dependencies(self, **kwargs):
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
            **kwargs
        )


class ProgramEvaluationObjetiveClient(EdFiAPIClient):
    endpoint = "programEvaluationObjectives"

    dependencies: Dict = {
        "edfi_performance_test.api.client.v5.program.ProgramEvaluationClient": {}
    }

    def create_with_dependencies(self, **kwargs):
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
            **kwargs
        )
