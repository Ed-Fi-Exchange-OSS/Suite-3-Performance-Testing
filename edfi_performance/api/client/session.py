from edfi_performance.api.client import EdFiAPIClient
from edfi_performance.api.client.grading_period import GradingPeriodClient
from edfi_performance.api.client.school import SchoolClient
from edfi_performance.factories.descriptors.utils import build_descriptor


class SessionClient(EdFiAPIClient):
    endpoint = 'sessions'

    dependencies = {
        GradingPeriodClient: {}
    }

    def create_with_dependencies(self, **kwargs):
        school_id = kwargs.pop('schoolId', SchoolClient.shared_elementary_school_id())

        # Create two grading periods
        period_1_reference = self.grading_period_client.create_with_dependencies(
            schoolReference__schoolId=school_id,
        )
        period_2_reference = self.grading_period_client.create_with_dependencies(
            schoolReference__schoolId=school_id,
            beginDate="2014-10-06",
            endDate="2014-12-15",
            totalInstructionalDays=30,
            gradingPeriodDescriptor=build_descriptor('GradingPeriod', 'Second Six Weeks')
        )

        # Create session referencing grading periods
        return self.create_using_dependencies(
            [{'period_1_reference': period_1_reference}, {'period_2_reference': period_2_reference}],
            schoolReference__schoolId=school_id,
            gradingPeriods__0__gradingPeriodReference__periodSequence=period_1_reference['attributes']['periodSequence'],
            gradingPeriods__1__gradingPeriodReference__periodSequence=period_2_reference['attributes']['periodSequence'],
            **kwargs)

    def delete_with_dependencies(self, reference, **kwargs):
        self.delete(reference['resource_id'])
        self.grading_period_client.delete_with_dependencies(reference['dependency_ids']['period_1_reference'])
        self.grading_period_client.delete_with_dependencies(reference['dependency_ids']['period_2_reference'])
