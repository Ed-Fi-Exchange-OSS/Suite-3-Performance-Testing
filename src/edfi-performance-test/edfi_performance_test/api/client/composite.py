# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import json

from typing import Dict
from edfi_performance_test.api.client.ed_fi_api_client import EdFiAPIClient


class EdFiCompositeClient(EdFiAPIClient):
    API_PREFIX: str  # Must be entered by the user. Should look like '/composites/v1/ed-fi/{compositeName}'
    factory = "None"
    constants: Dict

    def get_composite_list(self, resource_name, resource_id):
        response = self._get_response(
            "get",
            self._composite_list_endpoint(resource_name, resource_id),
            headers=self.get_headers(),
            name=self._composite_list_endpoint(resource_name, "{id}"),
        )
        if self.is_not_expected_result(response, [200]):
            return
        self.log_response(response)
        return json.loads(response.text)

    @classmethod
    def shared_id(cls, resource):
        if cls.constants[resource] is not None:
            return cls.constants[resource]
        client_instance = cls(cls.client, token=cls.token)
        cls.constants[resource] = client_instance._get_all(resource)[0]["id"]
        return cls.constants[resource]

    def _composite_list_endpoint(self, resource_name, resource_id):
        return "{}/{}/{}/{}".format(
            self.API_PREFIX, resource_name, resource_id, self.endpoint
        )

    def _get_all(self, resource):
        list_endpoint = "{}/{}".format(self.API_PREFIX, resource)
        response = self._get_response(
            "get", list_endpoint, headers=self.get_headers(), name=list_endpoint
        )
        self.log_response(response)
        return json.loads(response.text)
