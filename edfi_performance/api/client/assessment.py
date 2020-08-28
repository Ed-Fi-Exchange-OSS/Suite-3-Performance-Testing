# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from edfi_performance.api.client import EdFiAPIClient


class AssessmentClient(EdFiAPIClient):
    endpoint = 'assessments'


class AssessmentItemClient(EdFiAPIClient):
    endpoint = 'assessmentItems'

    dependencies = {
        AssessmentClient: {}
    }

    def create_with_dependencies(self, **kwargs):
        # Create new assessment
        assessment_reference = self.assessment_client.create_with_dependencies()

        # Create assessment item
        item_attrs = self.factory.build_dict(
            assessmentReference__assessmentTitle=assessment_reference['attributes']['assessmentTitle'],
            **kwargs
        )
        item_id = self.create(**item_attrs)

        return {
            'resource_id': item_id,
            'dependency_ids': {
                'assessment_reference': assessment_reference,
            },
            'attributes': item_attrs,
        }

    def delete_with_dependencies(self, reference, **kwargs):
        self.delete(reference['resource_id'])
        self.assessment_client.delete_with_dependencies(reference['dependency_ids']['assessment_reference'])


class LearningObjectiveClient(EdFiAPIClient):
    endpoint = 'learningObjectives'


class LearningStandardClient(EdFiAPIClient):
    endpoint = 'learningStandards'


class ObjectiveAssessmentClient(EdFiAPIClient):
    endpoint = 'objectiveAssessments'

    dependencies = {
        AssessmentClient: {}
    }

    def create_with_dependencies(self, **kwargs):
        # Create new assessment
        assessment_reference = self.assessment_client.create_with_dependencies()

        # Create objective assessment
        objective_attrs = self.factory.build_dict(
            assessmentReference__assessmentTitle=assessment_reference['attributes']['assessmentTitle'],
            **kwargs
        )
        objective_id = self.create(**objective_attrs)

        return {
            'resource_id': objective_id,
            'dependency_ids': {
                'assessment_reference': assessment_reference,
            },
            'attributes': objective_attrs,
        }

    def delete_with_dependencies(self, reference, **kwargs):
        self.delete(reference['resource_id'])
        self.assessment_client.delete_with_dependencies(reference['dependency_ids']['assessment_reference'])


class StudentAssessmentClient(EdFiAPIClient):
    endpoint = 'studentAssessments'

    dependencies = {
        AssessmentClient: {}
    }

    def create_with_dependencies(self, **kwargs):
        # Create new assessment
        assessment_reference = self.assessment_client.create_with_dependencies()

        # Create student assessment
        student_assessment_attrs = self.factory.build_dict(
            assessmentReference__assessmentTitle=assessment_reference['attributes']['assessmentTitle'],
            **kwargs
        )
        student_assessment_id = self.create(**student_assessment_attrs)

        return {
            'resource_id': student_assessment_id,
            'dependency_ids': {
                'assessment_reference': assessment_reference,
            },
            'attributes': student_assessment_attrs,
        }

    def delete_with_dependencies(self, reference, **kwargs):
        self.delete(reference['resource_id'])
        self.assessment_client.delete_with_dependencies(reference['dependency_ids']['assessment_reference'])
