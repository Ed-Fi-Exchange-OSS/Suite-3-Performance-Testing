from edfi_performance.api.client import EdFiAPIClient
from edfi_performance.api.client.grading_period import GradingPeriodClient


class ReportCardClient(EdFiAPIClient):
    endpoint = 'reportCards'

    dependencies = {
        GradingPeriodClient: {},
    }

    def create_with_dependencies(self, **kwargs):
        period_reference = self.grading_period_client.create_with_dependencies()

        return self.create_using_dependencies(
            period_reference,
            gradingPeriodReference__periodSequence=period_reference['attributes']['periodSequence'],
        )
