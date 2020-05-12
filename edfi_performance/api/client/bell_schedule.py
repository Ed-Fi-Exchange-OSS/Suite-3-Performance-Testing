from edfi_performance.api.client import EdFiAPIClient
from edfi_performance.api.client.class_period import ClassPeriodClient


class BellScheduleClient(EdFiAPIClient):
    endpoint = 'bellSchedules'

    dependencies = {
        ClassPeriodClient: {}
    }

    def create_with_dependencies(self, **kwargs):
        # Create new class period
        class_period_reference = self.class_period_client.create_with_dependencies()

        # Create bell schedule
        return self.create_using_dependencies(
            class_period_reference,
            classPeriods__0__classPeriodReference__classPeriodName=class_period_reference['attributes']['classPeriodName'],
            **kwargs
        )
