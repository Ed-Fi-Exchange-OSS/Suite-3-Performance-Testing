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
        return self.create_using_dependencies(
            assessment_reference,
            assessmentReference__assessmentIdentifier=assessment_reference['attributes']['assessmentIdentifier'],
            **kwargs
        )


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
        return self.create_using_dependencies(
            assessment_reference,
            assessmentReference__assessmentIdentifier=assessment_reference['attributes']['assessmentIdentifier'],
            **kwargs
        )


class StudentAssessmentClient(EdFiAPIClient):
    endpoint = 'studentAssessments'

    dependencies = {
        AssessmentClient: {}
    }

    def create_with_dependencies(self, **kwargs):
        # Create new assessment
        assessment_reference = self.assessment_client.create_with_dependencies()

        # Create student assessment
        return self.create_using_dependencies(
            assessment_reference,
            assessmentReference__assessmentIdentifier=assessment_reference['attributes']['assessmentIdentifier'],
            **kwargs
        )
