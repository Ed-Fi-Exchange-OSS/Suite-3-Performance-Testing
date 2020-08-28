# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

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
        schedule_attrs = self.factory.build_dict(
            classPeriods__0__classPeriodReference__classPeriodName=class_period_reference['attributes']['classPeriodName'],
            **kwargs
        )
        schedule_id = self.create(**schedule_attrs)

        return {
            'resource_id': schedule_id,
            'dependency_ids': {
                'class_period_reference': class_period_reference,
            },
            'attributes': schedule_attrs,
        }

    def delete_with_dependencies(self, reference, **kwargs):
        self.delete(reference['resource_id'])
        self.class_period_client.delete_with_dependencies(reference['dependency_ids']['class_period_reference'])
