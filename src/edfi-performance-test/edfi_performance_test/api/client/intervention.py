# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from edfi_performance_test.api.client.ed_fi_api_client import EdFiAPIClient


class InterventionPrescriptionClient(EdFiAPIClient):
    endpoint = "interventionPrescriptions"


class InterventionClient(EdFiAPIClient):
    endpoint = "interventions"

    dependencies = {
        InterventionPrescriptionClient: {
            "client_name": "prescription_client",
        }
    }

    def create_with_dependencies(self, **kwargs):
        # Create intervention prescription
        rx_reference = self.prescription_client.create_with_dependencies()
        if(rx_reference is None or rx_reference["resource_id"] is None):
            return

        # Create intervention
        return self.create_using_dependencies(
            rx_reference,
            interventionPrescriptions__0__interventionPrescriptionReference__interventionPrescriptionIdentificationCode=rx_reference[
                "attributes"
            ][
                "interventionPrescriptionIdentificationCode"
            ],
        )


class InterventionStudyClient(EdFiAPIClient):
    endpoint = "interventionStudies"

    dependencies = {
        InterventionPrescriptionClient: {
            "client_name": "prescription_client",
        }
    }

    def create_with_dependencies(self, **kwargs):
        # Create intervention prescription
        rx_reference = self.prescription_client.create_with_dependencies()
        if(rx_reference is None or rx_reference["resource_id"] is None):
            return

        # Create intervention
        return self.create_using_dependencies(
            rx_reference,
            interventionPrescriptionReference__interventionPrescriptionIdentificationCode=rx_reference[
                "attributes"
            ][
                "interventionPrescriptionIdentificationCode"
            ],
        )
