# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from typing import Dict
from edfi_performance_test.api.client.ed_fi_api_client import EdFiAPIClient


class AssessmentClientV5(EdFiAPIClient):
    endpoint = "assessments"


class AssessmentItemClientV5(EdFiAPIClient):
    endpoint = "assessmentItems"

    dependencies: Dict = {AssessmentClientV5: {}}

    def create_with_dependencies(self, **kwargs):
        # Create new assessment
        assessment_reference = self.assessment_client.create_with_dependencies()

        # Create assessment item
        return self.create_using_dependencies(
            assessment_reference,
            assessmentReference__assessmentIdentifier=assessment_reference[
                "attributes"
            ]["assessmentIdentifier"],
            **kwargs
        )


class LearningStandardClientV5(EdFiAPIClient):
    endpoint = "learningStandards"


class ObjectiveAssessmentClientV5(EdFiAPIClient):
    endpoint = "objectiveAssessments"

    dependencies: Dict = {AssessmentClientV5: {}}

    def create_with_dependencies(self, **kwargs):
        # Create new assessment
        assessment_reference = self.assessment_client.create_with_dependencies()

        # Create objective assessment
        return self.create_using_dependencies(
            assessment_reference,
            assessmentReference__assessmentIdentifier=assessment_reference[
                "attributes"
            ]["assessmentIdentifier"],
            **kwargs
        )


class StudentAssessmentClientV5(EdFiAPIClient):
    endpoint = "studentAssessments"

    dependencies: Dict = {AssessmentClientV5: {}}

    def create_with_dependencies(self, **kwargs):
        # Create new assessment
        assessment_reference = self.assessment_client.create_with_dependencies()

        # Create student assessment
        return self.create_using_dependencies(
            assessment_reference,
            assessmentReference__assessmentIdentifier=assessment_reference[
                "attributes"
            ]["assessmentIdentifier"],
            **kwargs
        )
