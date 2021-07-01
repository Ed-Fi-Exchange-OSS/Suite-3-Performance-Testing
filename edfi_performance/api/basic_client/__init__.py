# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import inspect
import logging
import urllib3
import json
import traceback

from locust.clients import HttpSession
from edfi_performance.config import get_config_value

logger = logging.getLogger('locust.runners')
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class EdFiBasicAPIClient(object):

    _http_client = None
    _token = None

    def __init__(self, api_prefix='/data/v3/ed-fi'):
        self.API_PREFIX = api_prefix
        host = get_config_value('host')
        self._http_client = HttpSession(host)
        # Suppress exceptions thrown in the Test Lab environment
        # when self-signed certificates are used.
        self._http_client.verify = False
        if self._token is None:
            self._token = self.login()

    def login(self, succeed_on=None, name=None, **credentials_overrides):
        if succeed_on is None:
            succeed_on = []
        name = name or '/oauth/token'
        payload = {
            "client_id": get_config_value('client_id'),
            "client_secret": get_config_value('client_secret'),
            "grant_type": "client_credentials",
        }
        payload.update(credentials_overrides)
        response = self._get_response(
            'post',
            "/oauth/token",
            payload,
            succeed_on=succeed_on,
            name=name)
        self.log_response(response, ignore_error=response.status_code in succeed_on)
        try:
            token = json.loads(response.text)["access_token"]
            return token
        except (KeyError, ValueError):
            # failed login
            return None

    def get_headers(self):
        if self._token is None:
            raise ValueError("Need to log in before getting authorization headers!")
        return {
            "Authorization": "Bearer {}".format(self._token),
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    def _get_response(self, method, *args, **kwargs):
        method = getattr(self._http_client, method)
        succeed_on = kwargs.pop('succeed_on', [])
        with method(*args, catch_response=True, allow_redirects=False, **kwargs) as response:
            if response.status_code in succeed_on:
                # If told explicitly to succeed, mark success
                response.success()
            elif 300 <= response.status_code < 400:
                # Mark 3xx Redirect responses as failure
                response.failure("Status code {} is a failure".format(response.status_code))
        # All other status codes are treated normally
        return response

    @staticmethod
    def log_response(response, ignore_error=False, log_response_text=False):
        if response.status_code >= 400 and not ignore_error:
            frame = inspect.currentframe(1)
            stack_trace = traceback.format_stack(frame)
            logger.error(u''.join(stack_trace))

        if log_response_text:
            logger.debug(response.text)

    @staticmethod
    def is_not_expected_result(response, expected_responses):
        if response.status_code not in expected_responses:
            message = 'Invalid response received'
            try:
                message = json.loads(response.text)['message']
            except Exception:
                pass
            print (response.request.method + " " + str(response.status_code) + ' : ' + message)
            return True
        return False

    def list_endpoint(self, endpoint, query=""):
        return "{}/{}{}".format(self.API_PREFIX, endpoint, query)

    def get_list(self, endpoint, query=""):
        response = self._get_response(
            'get',
            self.list_endpoint(endpoint, query),
            headers=self.get_headers(),
            name=self.list_endpoint(endpoint))
        if self.is_not_expected_result(response, [200]):
            return
        self.log_response(response)
        return json.loads(response.text)
