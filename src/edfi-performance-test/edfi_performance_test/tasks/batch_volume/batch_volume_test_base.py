# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# See the LICENSE and NOTICES files in the project root for more information.

from typing import Any, Dict, List

from locust import TaskSet

from edfi_performance_test.api.client.batch_api_client import BatchApiClient
from edfi_performance_test.helpers.config import get_config_value


class BatchVolumeTestBase(TaskSet):
    """
    Base TaskSet for DMS batch volume scenarios.

    Subclasses must define:
    - resource: str   # e.g. "students", "sections"
    - factory: Any    # factory with build_dict() to create documents
    - get_natural_key(document) -> Dict[str, Any]
      to provide the natural key used for update/delete.
    Optionally, subclasses can override build_update_document() to tweak the
    document used for the update operation.
    """

    resource: str = ""
    factory: Any = None
    batch_triple_count: int = 10

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        if not self.resource:
            raise RuntimeError(
                f"{self.__class__.__name__} must define a non-empty 'resource' name"
            )
        if self.factory is None:
            raise RuntimeError(
                f"{self.__class__.__name__} must define a 'factory' for building documents"
            )

        locust_http_client = getattr(getattr(self, "user", None), "client", None)
        if locust_http_client is None:
            raise RuntimeError(
                f"{self.__class__.__name__} requires a Locust user with an HTTP client"
            )

        base_url = get_config_value("PERF_API_BASEURL")

        token = getattr(self.user, "token", None)
        if not token:
            # Lazily obtain a token for this user if it has not been set yet.
            from edfi_performance_test.api.client.ed_fi_basic_api_client import (
                EdFiBasicAPIClient,
            )

            auth_client = EdFiBasicAPIClient(locust_http_client)
            token = auth_client.token
            setattr(self.user, "token", token)

        self._batch_client = BatchApiClient(
            client=locust_http_client,
            base_url=base_url,
            token=token,
        )

        self._batch_triple_count = self._determine_batch_triple_count()

    def _determine_batch_triple_count(self) -> int:
        default_value = str(getattr(self, "batch_triple_count", 10))
        value = get_config_value("PERF_BATCH_TRIPLE_COUNT", default_value)
        try:
            return int(value)
        except ValueError:
            return int(default_value)

    def build_create_op(self, resource: str, document: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "op": "create",
            "resource": resource,
            "document": document,
        }

    def build_update_op(
        self, resource: str, natural_key: Dict[str, Any], document: Dict[str, Any]
    ) -> Dict[str, Any]:
        return {
            "op": "update",
            "resource": resource,
            "naturalKey": natural_key,
            "document": document,
        }

    def build_delete_op(self, resource: str, natural_key: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "op": "delete",
            "resource": resource,
            "naturalKey": natural_key,
        }

    def get_natural_key(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """
        Subclasses must implement this to return the natural key for a document.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement get_natural_key()"
        )

    def build_update_document(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """
        Subclasses can override this to apply scenario-specific changes for the
        update operation. By default, this returns a shallow copy of the create
        document.
        """
        return dict(document)

    def run_triple_batch(self, resource: str, documents: List[Dict[str, Any]]) -> None:
        """
        Build and submit a batch consisting of create/update/delete triples
        for the given resource. The number of triples is controlled by the
        length of `documents`.
        """
        if not documents:
            return

        operations: List[Dict[str, Any]] = []

        for document in documents:
            natural_key = self.get_natural_key(document)
            create_document = document
            update_document = self.build_update_document(document)

            operations.append(self.build_create_op(resource, create_document))
            operations.append(self.build_update_op(resource, natural_key, update_document))
            operations.append(self.build_delete_op(resource, natural_key))

        request_name = f"{resource}-batch-{len(documents)}"
        self._batch_client.post_batch(operations, name=request_name)

