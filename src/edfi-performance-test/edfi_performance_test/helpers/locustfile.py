# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from urllib import response
from locust import HttpUser, task
import json

class HelloWorldUser(HttpUser):
    #client = None
    host="http://localhost:54746"
    API_PREFIX = "/data/v3/ed-fi"

    @task
    def get_students(self):
        self.get_list("students")

    @task
    def login(self, succeed_on=None, name=None):
        if succeed_on is None:
            succeed_on = []
        payload = {
            "client_id": 'emptyKey',
            "client_secret": 'emptysecret',
            "grant_type": "client_credentials",
        }
        response = self._get_response(
            'post',
            "/oauth/token",
            payload,
            succeed_on=succeed_on,
            name=name)

        try:
            self.token = json.loads(response.text)["access_token"]
            return self.token
        except (KeyError, ValueError):
            # failed login
            return None

    def _get_response(self, method, *args, **kwargs):
        self.client.verify = False
        method = getattr(self.client, method)
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

    def get_headers(self):
        if self.token is None:
            raise ValueError("Need to log in before getting authorization headers!")
        return {
            "Authorization": "Bearer {}".format(self.token),
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

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
        #self.log_response(response)
        return json.loads(response.text)
