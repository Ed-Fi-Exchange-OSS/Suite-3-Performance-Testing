# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from edfi_performance.api.client import EdFiAPIClient
from edfi_performance.api.client.grading_period import GradingPeriodClient


class ReportCardClient(EdFiAPIClient):
    endpoint = 'reportCards'

    dependencies = {
        GradingPeriodClient: {},
    }

    def create_with_dependencies(self, **kwargs):
        period_reference = self.grading_period_client.create_with_dependencies()

        card_attrs = self.factory.build_dict(
            gradingPeriodReference__periodSequence=period_reference['attributes']['periodSequence'],
        )
        card_id = self.create(**card_attrs)

        return {
            'resource_id': card_id,
            'dependency_ids': {
                'period_reference': period_reference,
            },
            'attributes': card_attrs,
        }

    def delete_with_dependencies(self, reference, **kwargs):
        self.delete(reference['resource_id'])
        self.grading_period_client.delete_with_dependencies(reference['dependency_ids']['period_reference'])
