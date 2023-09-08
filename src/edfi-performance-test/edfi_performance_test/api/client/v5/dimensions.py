# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from typing import Dict

from edfi_performance_test.api.client.ed_fi_api_client import EdFiAPIClient
from edfi_performance_test.api.client.v5.program import ProgramEvaluationElementClient


class EvaluationRubricDimensionClient(EdFiAPIClient):
    endpoint = "evaluationRubricDimensions"

    dependencies: Dict = {ProgramEvaluationElementClient: {}}

    def create_with_dependencies(self, **kwargs):
        eval_ref = self.program_evaluation_element_client.create_with_dependencies()

        return self.create_using_dependencies(
            eval_ref,
            programEvaluationElementReference__programEducationOrganizationId=eval_ref[
                "attributes"]
            ["programEvaluationReference"]["programEducationOrganizationId"],
            programEvaluationElementReference__ProgramEvaluationElementTitle=eval_ref[
                "attributes"]["programEvaluationElementTitle"],
            programEvaluationElementReference__programEvaluationPeriodDescriptor=eval_ref[
                "attributes"]
            ["programEvaluationReference"]["programEvaluationPeriodDescriptor"],
            programEvaluationElementReference__programEvaluationTitle=eval_ref[
                "attributes"]
            ["programEvaluationReference"]["programEvaluationTitle"],
            programEvaluationElementReference__programEvaluationTypeDescriptor=eval_ref[
                "attributes"]
            ["programEvaluationReference"]["programEvaluationTypeDescriptor"],
            programEvaluationElementReference__programName=eval_ref[
                "attributes"]
            ["programEvaluationReference"]["programName"],
            programEvaluationElementReference__programTypeDescriptor=eval_ref[
                "attributes"]
            ["programEvaluationReference"]["programTypeDescriptor"],
            ** kwargs
        )
