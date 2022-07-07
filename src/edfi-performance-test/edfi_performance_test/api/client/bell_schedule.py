# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from typing import Dict
from edfi_performance_test.api.client.ed_fi_api_client import EdFiAPIClient
from edfi_performance_test.api.client.class_period import ClassPeriodClient


class BellScheduleClient(EdFiAPIClient):
    endpoint = 'bellSchedules'

    dependencies: Dict = {
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
