# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import json

from edfi_performance.api.client import EdFiAPIClient, get_config_value


class EdFiCompositeClient(EdFiAPIClient):
    API_PREFIX = None  # Must be entered by the user. Should look like '/composites/v3/ed-fi/{compositeName}'
    factory = 'None'
    constants = None

    def get_composite_list(self, resource_name, resource_id):
        response = self._get_response(
            'get',
            self._composite_list_endpoint(resource_name, resource_id),
            headers=self.get_headers(),
            name=self._composite_list_endpoint(resource_name, '{id}'))
        if self.is_not_expected_result(response, [200]):
            return
        self.log_response(response)
        return json.loads(response.text)

    @classmethod
    def shared_id(cls, resource):
        if cls.constants[resource] is not None:
            return cls.constants[resource]
        client_instance = cls(get_config_value('host'), token=cls.token)
        cls.constants[resource] = client_instance._get_all(resource)[0]['id']
        return cls.constants[resource]

    def _composite_list_endpoint(self, resource_name, resource_id):
        return "{}/{}/{}/{}".format(self.API_PREFIX, resource_name, resource_id, self.endpoint)

    def _get_all(self, resource):
        list_endpoint = "{}/{}".format(self.API_PREFIX, resource)
        response = self._get_response(
            'get',
            list_endpoint,
            headers=self.get_headers(),
            name=list_endpoint)
        self.log_response(response)
        return json.loads(response.text)
