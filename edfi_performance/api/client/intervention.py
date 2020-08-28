# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from edfi_performance.api.client import EdFiAPIClient


class InterventionPrescriptionClient(EdFiAPIClient):
    endpoint = 'interventionPrescriptions'


class InterventionClient(EdFiAPIClient):
    endpoint = 'interventions'

    dependencies = {
        InterventionPrescriptionClient: {
            'client_name': 'prescription_client',
        }
    }

    def create_with_dependencies(self, **kwargs):
        # Create intervention prescription
        rx_reference = self.prescription_client.create_with_dependencies()

        # Create intervention
        intervention_attrs = self.factory.build_dict(
            interventionPrescriptions__0__interventionPrescriptionReference__interventionPrescriptionIdentificationCode=
            rx_reference['attributes']['interventionPrescriptionIdentificationCode'],
        )
        intervention_id = self.create(**intervention_attrs)

        return {
            'resource_id': intervention_id,
            'dependency_ids': {
                'rx_reference': rx_reference,
            },
            'attributes': intervention_attrs,
        }

    def delete_with_dependencies(self, reference, **kwargs):
        self.delete(reference['resource_id'])
        self.prescription_client.delete_with_dependencies(reference['dependency_ids']['rx_reference'])


class InterventionStudyClient(EdFiAPIClient):
    endpoint = 'interventionStudies'

    dependencies = {
        InterventionPrescriptionClient: {
            'client_name': 'prescription_client',
        }
    }

    def create_with_dependencies(self, **kwargs):
        # Create intervention prescription
        rx_reference = self.prescription_client.create_with_dependencies()

        # Create intervention
        study_attrs = self.factory.build_dict(
            interventionPrescriptionReference__interventionPrescriptionIdentificationCode=
            rx_reference['attributes']['interventionPrescriptionIdentificationCode'],
        )
        study_id = self.create(**study_attrs)

        return {
            'resource_id': study_id,
            'dependency_ids': {
                'rx_reference': rx_reference,
            },
            'attributes': study_attrs,
        }

    def delete_with_dependencies(self, reference, **kwargs):
        self.delete(reference['resource_id'])
        self.prescription_client.delete_with_dependencies(reference['dependency_ids']['rx_reference'])
