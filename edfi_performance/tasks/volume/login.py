from locust import task

from edfi_performance.api.client import EdFiAPIClient
from edfi_performance.tasks.volume import EdFiVolumeTestBase


class LoginVolumeTest(EdFiVolumeTestBase):
    client_class = EdFiAPIClient

    endpoint_name = "/oauth/token [LoginVolumeTest]"

    @task(weight=2)
    def successful_login(self):
        response = self.client.login(name=self.endpoint_name)
        assert response is not None

    @task(weight=1)
    def unsuccessful_login(self):
        response = self.client.login(
            client_id="bad_client",
            client_secret="bad_secret",
            succeed_on=[400],
            name=self.endpoint_name,
        )
        assert response is None
