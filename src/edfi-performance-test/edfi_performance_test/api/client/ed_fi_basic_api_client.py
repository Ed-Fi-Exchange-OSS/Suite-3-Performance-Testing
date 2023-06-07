# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import inspect
import logging
import urllib3
import json
import traceback
from os import _exit

from urllib3.exceptions import InsecureRequestWarning
from locust.clients import HttpSession
from requests import Response

from edfi_performance_test.helpers.config import (
    get_config_value,
    DEFAULT_API_PREFIX,
    DEFAULT_OAUTH_ENDPOINT,
)

logger = logging.getLogger("locust.runners")
urllib3.disable_warnings(InsecureRequestWarning)


class EdFiBasicAPIClient:

    def __init__(
        self, client: HttpSession, token: str = "", api_prefix="", endpoint=""
    ):
        self.api_prefix: str = api_prefix or get_config_value(
            "PERF_API_PREFIX", DEFAULT_API_PREFIX
        )
        self.oauth_endpoint = get_config_value(
            "PERF_API_OAUTH_ENDPOINT", DEFAULT_OAUTH_ENDPOINT
        )
        self.endpoint = endpoint
        self.client = client
        # Suppress exceptions thrown in the Test Lab environment
        # when self-signed certificates are used.
        self.client.verify = not eval(get_config_value("IGNORE_TLS_CERTIFICATE"))

        self.token = token or self.login()

    def login(self) -> str:
        """
        Attempt to login to the Ed-Fi API. If login fails, exit the program in
        order to avoid an infinite loop of login attempts.
        """

        payload = {
            "client_id": get_config_value("PERF_API_KEY"),
            "client_secret": get_config_value("PERF_API_SECRET"),
            "grant_type": "client_credentials",
        }

        try:
            response = self._post(self.oauth_endpoint, payload)

            if response.status_code != 200:
                logger.fatal("Login failed with status code %s for URL %s %s", response.status_code, response.url, response.text)

                # Stop the application, not just the running thread, by using _exit() instead of exit()
                _exit(1)
        except BaseException as e:
            logger.fatal("Login failed %s", e)
            _exit(1)

        # Let any exception bubble up
        self.token = json.loads(response.text)["access_token"]
        return self.token

    def get_headers(self):
        if self.token is None:
            self.token = self.login()
        return {
            "Authorization": "Bearer {}".format(self.token),
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    def _post(self, endpoint: str, payload: dict) -> Response:

        # Make sure the endpoint begins with a slash
        if not endpoint.endswith("/"):
            endpoint = f"{endpoint}/"

        response: Response = self.client.request("post", endpoint, data=payload)

        self.log_response(response)

        if response.status_code == 401 and "/token" not in response.url:
            # If token expired, re-login. But 401 on the token endpoint should NOT cause a retry.
            self.token = self.login()
            response = self._post(endpoint, payload)

        # All other status codes are treated normally
        return response

    def _get_response(self, method_name, *args, **kwargs):
        method = getattr(self.client, method_name)
        succeed_on = kwargs.pop("succeed_on", [])
        with method(
            *args, catch_response=True, allow_redirects=False, **kwargs
        ) as response:
            if response.status_code == 401:  # If token expired, re-login
                self.token = self.login()
                kwargs["headers"] = self.get_headers()
                response = self._get_response(method_name, *args, **kwargs)
            if response.status_code in succeed_on:
                # If told explicitly to succeed, mark success
                response.success()
            elif 300 <= response.status_code < 400:
                # Mark 3xx Redirect responses as failure
                response.failure(
                    "Status code {} is a failure".format(response.status_code)
                )
        # All other status codes are treated normally
        return response

    @staticmethod
    def log_response(response, ignore_error=False, log_response_text=False):
        if response.status_code >= 400 and not ignore_error:
            frame = inspect.currentframe()
            stack_trace = traceback.format_stack(frame)
            logger.error("".join(stack_trace))

        if log_response_text:
            logger.debug(response.text)

    @staticmethod
    def is_not_expected_result(response, expected_responses):
        if response.status_code not in expected_responses:
            print(
                f"{response.request.method} {response.request.url} - RESPONSE CODE: {response.status_code} : {response.text}"
            )
            return True
        return False

    def list_endpoint(self, query=""):
        return "{}/{}{}".format(self.api_prefix, self.endpoint, query)

    def get_list(self, query=""):
        # 287 - Pipeclean
        if "NoEndpoint" in self.endpoint:
            return
        response = self._get_response(
            "get",
            self.list_endpoint(query),
            headers=self.get_headers(),
            name=self.list_endpoint(),
        )
        if self.is_not_expected_result(response, [200]):
            return
        self.log_response(response)
        return json.loads(response.text)
