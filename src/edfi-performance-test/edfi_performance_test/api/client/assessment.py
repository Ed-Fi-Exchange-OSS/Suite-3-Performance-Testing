# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from typing import Dict
from edfi_performance_test.api.client.ed_fi_api_client import EdFiAPIClient


class AssessmentClient(EdFiAPIClient):
    endpoint = "assessments"


class AssessmentItemClient(EdFiAPIClient):
    endpoint = "assessmentItems"

    dependencies: Dict = {AssessmentClient: {}}

    def create_with_dependencies(self, **kwargs):
        # Create new assessment
        assessment_reference = self.assessment_client.create_with_dependencies()  # type: ignore

        # Create assessment item
        return self.create_using_dependencies(
            assessment_reference,
            assessmentReference__assessmentIdentifier=assessment_reference[
                "attributes"
            ]["assessmentIdentifier"],
            **kwargs
        )


class LearningObjectiveClient(EdFiAPIClient):
    endpoint = "learningObjectives"


class LearningStandardClient(EdFiAPIClient):
    endpoint = "learningStandards"


class ObjectiveAssessmentClient(EdFiAPIClient):
    endpoint = "objectiveAssessments"

    dependencies: Dict = {AssessmentClient: {}}

    def create_with_dependencies(self, **kwargs):
        # Create new assessment
        assessment_reference = self.assessment_client.create_with_dependencies()  # type: ignore

        # Create objective assessment
        return self.create_using_dependencies(
            assessment_reference,
            assessmentReference__assessmentIdentifier=assessment_reference[
                "attributes"
            ]["assessmentIdentifier"],
            **kwargs
        )


class StudentAssessmentClient(EdFiAPIClient):
    endpoint = "studentAssessments"

    dependencies: Dict = {AssessmentClient: {}}

    def create_with_dependencies(self, **kwargs):
        # Create new assessment
        assessment_reference = self.assessment_client.create_with_dependencies() # type: ignore

        # Create student assessment
        return self.create_using_dependencies(
            assessment_reference,
            assessmentReference__assessmentIdentifier=assessment_reference[
                "attributes"
            ]["assessmentIdentifier"],
            **kwargs
        )
