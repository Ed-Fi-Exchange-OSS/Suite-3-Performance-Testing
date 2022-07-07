# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from typing import Dict
from edfi_performance_test.api.client.ed_fi_api_client import EdFiAPIClient
from edfi_performance_test.api.client.grading_period import GradingPeriodClient


class ReportCardClient(EdFiAPIClient):
    endpoint = 'reportCards'

    dependencies : Dict = {
        GradingPeriodClient: {},
    }

    def create_with_dependencies(self, **kwargs):
        period_reference = self.grading_period_client.create_with_dependencies()

        return self.create_using_dependencies(
            period_reference,
            gradingPeriodReference__periodSequence=period_reference['attributes']['periodSequence'],
        )
