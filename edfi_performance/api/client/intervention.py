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
        return self.create_using_dependencies(
            rx_reference,
            interventionPrescriptions__0__interventionPrescriptionReference__interventionPrescriptionIdentificationCode=
            rx_reference['attributes']['interventionPrescriptionIdentificationCode'],
        )


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
        return self.create_using_dependencies(
            rx_reference,
            interventionPrescriptionReference__interventionPrescriptionIdentificationCode=
            rx_reference['attributes']['interventionPrescriptionIdentificationCode'],
        )
