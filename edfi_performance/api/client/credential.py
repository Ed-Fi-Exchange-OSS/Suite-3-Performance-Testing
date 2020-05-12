from edfi_performance.api.client import EdFiAPIClient


class CredentialClient(EdFiAPIClient):
    endpoint = 'credentials'
