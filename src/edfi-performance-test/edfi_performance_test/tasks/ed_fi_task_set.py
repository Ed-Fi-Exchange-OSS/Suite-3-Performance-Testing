# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from typing import Callable
from locust import TaskSet

from edfi_performance_test.api.client.ed_fi_api_client import (
    import_from_dotted_path,
    EdFiAPIClient,
)


class EdFiTaskSet(TaskSet):
    """
    Wraps `locust.TaskSet` to provide an API client specific to EdFi resources
    and descriptors.

    Required attributes on subclasses:
    - client_class: An `EdFiAPIClient` subclass specific to the resource being
      tested in this class's tasks

    Attributes passed through to the API client, and which can be used as if
    they existed on this class:
    - `factory`: The `APIFactory` subclass which builds resources
    - CRUD verbs: `get_list`, `get_detail`, `create`, `update`, `delete`
    - Sub-clients: Dependent clients of `client_class`

    Usage:
    ```python
    class ExampleTest(EdFiTaskSet):
        client_class = ExampleClient            # Assume has a dependency called `student_client`

        @task
        def run_example_scenario(self):
            self.get_list()                     # Passed through to API client `get_list()
            id = self.create()                  # Passed through to API client `create()`
                                                # with default attributes from client's factory
            attrs = self.factory.build_dict()   # Passed through to API client factory
            attrs['exampleAttr'] = 'somethingElse'
            s_id = self.student_client.create() # Passed through to API client `student_client`
            self.update(id, **attrs)            # Passed through to API client `update()`
            self.delete(id)                     # Passed through to API client `delete()`
            self.student_client.delete(s_id)
    ```
    """

    client_class: Callable = type(None)

    _api_client: EdFiAPIClient

    def __init__(self, parent, *args, **kwargs):
        if type(self) is EdFiTaskSet:
            raise NotImplementedError(
                "Abstract class EdFiTaskSet cannot be instantiated"
            )

        super(EdFiTaskSet, self).__init__(parent, *args, **kwargs)

        self.generate_client_class()

        self._api_client = self.client_class(
            client=EdFiAPIClient.client, token=EdFiAPIClient.token
        )

    def __getattr__(self, item):
        # Pass some attributes through to the EdFiAPIClient
        if (
            item
            in [  # CRUD calls
                "login",
                "get_item",
                "get_list",
                "create",
                "update",
                "delete",
                "get_composite_list",
            ]
            or item == "factory"
            or item == "request_name"
            or item.endswith("_client")  # Factory instance  # Dependency client
        ):
            return getattr(self._api_client, item)
        raise AttributeError(
            "'{}' object has no attribute '{}'".format(self.__class__.__name__, item)
        )

    @property
    def client(self):
        # Overwrite Locust client with EdFiAPIClient instance
        return self._api_client

    def create_with_dependencies(self, client_class=None, **kwargs):
        """
        Atomically creates an instance of `client_class` with default values,
        including all dependencies.  Returns a reference (defined by client
        class) which can be used to atomically delete this instance and its
        dependencies.

        :param client_class: The class of the client for the resource being
          created, or `None` for this task set's client.  NB: Currently, the
          only client class which can be passed to this is `SectionClient`.
        :param kwargs: Keyword arguments to `client_class.create_with_dependencies()`.
        :return: Reference which can be passed to `delete_from_reference`
        """
        if client_class is None:
            client_class = self.client_class
        client_instance = client_class(
            self._api_client.client, token=self._api_client.token
        )
        return client_instance.create_with_dependencies(**kwargs)

    def delete_from_reference(self, reference, client_class=None):
        """
        Atomically deletes an instance of `client_class` from a reference
        returned from `create_with_dependencies` for the same client class.

        :param reference: Reference from `create_with_dependencies`
        :param client_class: See `create_with_dependencies` above.
        :return: Return value of client class's `delete_with_dependencies`, usually
          `None`.
        """
        if client_class is None:
            client_class = self.client_class
        client_instance = client_class(
            self._api_client.client, token=self._api_client.token
        )
        return client_instance.delete_with_dependencies(reference)

    def generate_client_class(self):
        if isinstance(self.client_class, type(None)):
            return
        if "pipeclean" in self.__class__.__module__:
            class_name = self.__class__.__name__.replace("PipecleanTest", "Client")
            class_path = (
                self.__class__.__module__.replace("tasks.pipeclean", "api.client")
                + "."
                + class_name
            )
        elif "volume" in self.__class__.__module__:
            class_name = self.__class__.__name__.replace("VolumeTest", "Client")
            class_path = (
                self.__class__.__module__.replace("tasks.volume", "api.client")
                + "."
                + class_name
            )
        elif "change_query" in self.__class__.__module__:
            class_name = self.__class__.__name__.replace("ChangeQueryTest", "Client")
            class_path = (
                self.__class__.__module__.replace("tasks.change_query", "api.client")
                + "."
                + class_name
            )
        else:
            raise RuntimeError("Cannot determine class_name and class_path")

        self.client_class = import_from_dotted_path(class_path)

    @staticmethod
    def is_invalid_response(resource_id):
        if resource_id is None:
            return True
        return False
