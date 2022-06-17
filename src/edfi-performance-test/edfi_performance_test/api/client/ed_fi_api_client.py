# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import importlib
import inspect
import json
import logging
import re
import traceback
from typing import Any, Dict

import urllib3
from urllib3.exceptions import InsecureRequestWarning

from edfi_performance_test.helpers.config import get_config_value

logger = logging.getLogger("locust.runners")

# Suppress warnings logged to the console in the Test Lab environment
# when self-signed certificates are used.
urllib3.disable_warnings(InsecureRequestWarning)


class EdFiAPIClient:
    """
    Wraps the Locust HTTP client with some Ed-Fi specific logic.  Use this
    class to create, read, update, and delete Ed-Fi resources.

    Required attributes on subclasses:
    - endpoint: The resource name in the API endpoint URL, e.g. 'students'
    - factory: An `APIFactory` subclass representing this resource, e.g.
        StudentFactory.

    The `dependencies` attribute allows use of clients for other resources in
    case those are needed (e.g., in the case of Student, a
    StudentSchoolAssociation to a school is necessary for the Ed-Fi ODS API
    to allow updates to the student.)

    Keys in the `dependencies` dict are class names for other clients, either
    imported or in dotted-path string format.  Values are options dictionaries,
    with the following options available.
    - 'client_name': Override the default name given the client.  By default,
        the client will be created as an attribute on this client based on the
        class name, e.g. FooBarClient => self.foo_bar_client.

    Usage:
    ```
    class SchoolClient(EdFiAPIClient):
        endpoint = 'schools'
        factory = SchoolFactory

    class ReallyLongNameClient(EdFiAPIClient):
        endpoint = ...
        factory = ...

    class DependencyClient(EdFiAPIClient):
        endpoint = ...
        factory = ...

        dependencies = {
            SchoolClient: {},                   # Creates `self.school_client`
            ReallyLongNameClient: {
                'client_name': 'name_client'    # Creates `self.name_client`
                                                # (default would be `self.really_long_name_client`)
            }
        }

        def create_with_dependencies(self, **kwargs):
            ...
            school_id = self.school_client.create_with_dependencies()
            name_id = self.name_client.create_with_dependencies()
            ...
    ```
    """

    API_PREFIX = "/data/v3/ed-fi"

    factory: Any
    endpoint: str

    dependencies: Dict = {}

    token: str

    def __init__(self, client, token: str = ""):
        # super().__init__(client.base_url,client.request_event,client.user)
        self.token = token
        self.client = client

        # Suppress exceptions thrown in the Test Lab environment
        # when self-signed certificates are used.
        self.client.verify = False

        token = token or self.login()
        EdFiAPIClient.token = token
        EdFiAPIClient.client = client

        for subclient_class, options in self.dependencies.items():
            if isinstance(subclient_class, str):
                subclient_class = import_from_dotted_path(subclient_class)
            subclient_name = options.get("client_name")
            if subclient_name is None:
                # Default to FooClient => foo_client
                subclient_name = _title_case_to_snake_case(subclient_class.__name__)

            client = subclient_class(client, token=token)
            setattr(self, subclient_name, client)

        self.generate_factory_class()

    @staticmethod
    def log_response(response, ignore_error=False, log_response_text=False):
        if response.status_code >= 400 and not ignore_error:
            frame = inspect.currentframe()
            stack_trace = traceback.format_stack(frame)
            logger.error("".join(stack_trace))

        if log_response_text:
            logger.debug(response.text)

    def list_endpoint(self, query=""):
        return "{}/{}{}".format(self.API_PREFIX, self.endpoint, query)

    def detail_endpoint(self, resource_id):
        return "{}/{}".format(self.list_endpoint(), resource_id)

    def detail_endpoint_nickname(self):
        return self.detail_endpoint("{id}")

    def _get_response(self, method, *args, **kwargs):
        method = getattr(self.client, method)
        succeed_on = kwargs.pop("succeed_on", [])
        with method(
            *args, catch_response=True, allow_redirects=False, **kwargs
        ) as response:
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

    def login(self, succeed_on=None, name=None, **credentials_overrides) -> str:
        if succeed_on is None:
            succeed_on = []
        name = name or "/oauth/token"
        payload = {
            "client_id": get_config_value("key"),
            "client_secret": get_config_value("secret"),
            "grant_type": "client_credentials",
        }
        payload.update(credentials_overrides)
        response = self._get_response(
            "post", "/oauth/token", payload, succeed_on=succeed_on, name=name
        )
        self.log_response(response, ignore_error=response.status_code in succeed_on)
        try:
            self.token = json.loads(response.text)["access_token"]
            return self.token
        except (KeyError, ValueError):
            # failed login
            raise RuntimeError("Login failed")

    def get_headers(self):
        token = self.token
        if token is None:
            raise ValueError("Need to log in before getting authorization headers!")
        return {
            "Authorization": "Bearer {}".format(token),
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    def get_list(self, query=""):
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

    def get_item(self, resource_id):
        response = self._get_response(
            "get",
            self.detail_endpoint(resource_id),
            headers=self.get_headers(),
            name=self.detail_endpoint_nickname(),
        )
        if self.is_not_expected_result(response, [200]):
            return
        self.log_response(response)
        return json.loads(response.text)

    def create(self, unique_id_field=None, name=None, **factory_kwargs):
        # Pass in a `unique_id_field` name (e.g. 'schoolId') to have that
        # attribute returned alongside the resource_id.  Useful if you need
        # an association to this resource.
        unique_id = None
        succeed_on = factory_kwargs.pop("succeed_on", [])
        name = name or self.list_endpoint()
        payload = self.factory.build_json(**factory_kwargs)
        if unique_id_field:
            unique_id = json.loads(payload)[unique_id_field]
        response = self._get_response(
            "post",
            self.list_endpoint(),
            data=payload,
            headers=self.get_headers(),
            succeed_on=succeed_on,
            name=name,
        )
        if response.status_code in succeed_on:
            return
        if succeed_on != [] and response.status_code not in succeed_on:
            response.failure("Status code {} is a failure".format(response.status_code))
            return
        if self.is_not_expected_result(response, [200, 201]):
            if unique_id is not None:
                return None, None
            return None
        self.log_response(response)
        resource_id = response.headers["Location"].split("/")[-1].strip()
        if unique_id is not None:
            return resource_id, unique_id
        return resource_id

    def update(self, resource_id, **update_kwargs):
        # Be sure to pass in a fully defined object; ODS doesn't allow partial updates.
        payload = self.factory.build_json(**update_kwargs)
        response = self._get_response(
            "put",
            self.detail_endpoint(resource_id),
            data=payload,
            headers=self.get_headers(),
            name=self.detail_endpoint_nickname(),
        )
        if self.is_not_expected_result(response, [200, 204]):
            return
        self.log_response(response)
        new_id = response.headers["Location"].split("/")[-1].strip()
        assert new_id == resource_id
        return resource_id

    def delete_item(self, resource_id):
        if get_config_value("deleteResources").lower() == "false":
            logger.debug(
                "Skipping delete of {} instance {} because"
                " deleteResources=False".format(
                    self.__class__.__name__.replace("Client", ""), resource_id
                )
            )
            return True
        response = self._get_response(
            "delete",
            self.detail_endpoint(resource_id),
            headers=self.get_headers(),
            name=self.detail_endpoint_nickname(),
        )
        if self.is_not_expected_result(response, [204]):
            return
        self.log_response(response)
        return response.status_code == 204

    def create_with_dependencies(self, **kwargs):
        """
        Atomically create an instance of this resource along with all
        dependencies.  This method will be called by `EdFiTaskSet` scenarios
        as well as by dependent clients.  It should return a reference object
        which `delete_with_dependencies` can use to atomically delete the created
        resource plus dependencies.

        Recommended format for a reference dictionary is:
        {
            'resource_id': 1,               # ID of created resource
            'dependency_ids': {
                'school_id': 23498,         # ID of dependent resource 1
                'student_id': a9cd,         # ID of dependent resource 2
                ...
            },
            'attributes': {                 # Attributes dict by which the resource can be recreated or updated
                'beginDate': '2018-01-01',
                'endDate': '2018-02-01',
                ...
            },
            ...                             # Any ODS reference IDs can be added here for dependent clients' use
        }

        :param kwargs: Overrides to default factory attributes for resource
        :return: Reference to this resource and dependencies (see above)
        """
        resource_attrs = self.factory.build_dict(**kwargs)
        resource_id = self.create(**resource_attrs)
        return {
            "resource_id": resource_id,
            "attributes": resource_attrs,
        }

    def create_using_dependencies(self, dependency_reference=None, **kwargs):
        resource_attrs = self.factory.build_dict(**kwargs)
        resource_id = self.create(**resource_attrs)

        if isinstance(dependency_reference, list):
            dependencies = {}
            for obj in dependency_reference:
                key, value = obj.items()[0]
                dependencies[key] = value

            return {
                "resource_id": resource_id,
                "dependency_ids": dependencies,
                "attributes": resource_attrs,
            }

        return {
            "resource_id": resource_id,
            "dependency_ids": {
                "dependency_reference": dependency_reference,
            },
            "attributes": resource_attrs,
        }

    def delete_with_dependencies(self, reference, **kwargs):
        """
        Atomically delete an instance of this resource along with all
        dependencies.  The `reference` parameter will contain the necessary
        information (see `create_with_dependencies` above for the recommended format,
        but it can be anything as long as `create_with_dependencies, `delete_with_dependencies`,
        and all consumers of this client agree on it.

        :param reference: Reference to this resource + dependencies (see above)
        :param kwargs: Currently unused
        :return: `None`
        """
        self.delete_item(reference["resource_id"])
        if len(self.dependencies) == 1:
            self._get_dependency_client().delete_with_dependencies(
                reference["dependency_ids"]["dependency_reference"]
            )
        elif len(self.dependencies) > 1:
            for dependency in reference["dependency_ids"]:
                getattr(self, dependency).delete_with_dependencies(
                    reference["dependency_ids"][dependency]
                )

    def _get_dependency_client(self):
        subclient_class, client_name = self.dependencies.items()[0]  # type: ignore
        if isinstance(subclient_class, str):
            subclient_class = import_from_dotted_path(subclient_class)
        subclient_name = client_name.get("client_name")
        if subclient_name is None:
            subclient_name = _title_case_to_snake_case(subclient_class.__name__)
        return getattr(self, subclient_name)

    @classmethod
    def create_shared_resource(cls, value, **kwargs):
        client_instance = cls(cls.client, token=cls.token)
        resource_reference = client_instance.create_with_dependencies(**kwargs)
        return resource_reference["attributes"][value]

    def generate_factory_class(self):
        if self.factory is not None or self.__class__.__name__ == "EdFiAPIClient":
            return
        class_name = self.__class__.__name__.replace("Client", "Factory")
        class_path = (
            self.__class__.__module__.replace("api.client", "factories.resources")
            + "."
            + class_name
        )
        self.factory = import_from_dotted_path(class_path)

    @staticmethod
    def is_not_expected_result(response, expected_responses):
        if response.status_code not in expected_responses:
            message = "Invalid response received"
            try:
                message = json.loads(response.text)["message"]
            except Exception:
                pass
            print(
                response.request.method
                + " "
                + str(response.status_code)
                + " : "
                + message
            )
            return True
        return False


def _title_case_to_snake_case(name):
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def import_from_dotted_path(path) -> Any:
    parts = path.split(".")
    module_path = ".".join(parts[:-1])
    module = importlib.import_module(module_path)
    return getattr(module, parts[-1])
