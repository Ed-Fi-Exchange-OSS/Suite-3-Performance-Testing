# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# See the LICENSE and NOTICES files in the project root for more information.

"""
Manual integration-style test for the DMS /batch endpoint using the Student
resource.

This script is not invoked by the automated test suite. It is intended to be
run manually against a running DMS instance to verify that a simple
create/update/delete triple for students succeeds via the /batch endpoint.

Usage example (from src/edfi-performance-test/):

    PERF_API_BASEURL=https://localhost:54746 \\
    PERF_API_KEY=testkey \\
    PERF_API_SECRET=testsecret \\
    PERF_API_OAUTH_ENDPOINT=/oauth/token \\
    IGNORE_TLS_CERTIFICATE=True \\
    poetry run python -m edfi_performance_test.manual_student_batch_integration
"""

import json
import os
from typing import Any, Dict, Optional

import requests
from dotenv import load_dotenv, find_dotenv

from edfi_performance_test.api.client.batch_api_client import BatchApiClient


class RequestsResponseContext:
    """
    Minimal context manager adapter to satisfy the interface expected by
    BatchApiClient._send_request, using the `requests` library under the hood.
    """

    def __init__(self, response: requests.Response) -> None:
        self._response = response
        self.status_code = response.status_code
        self.text = response.text
        self.headers = response.headers
        self.request = response.request

    def failure(self, message: str) -> None:
        print(f"[batch failure] {message}")

    def __enter__(self) -> "RequestsResponseContext":
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        return False


class RequestsHttpSessionAdapter:
    """
    Simple adapter that presents a `request` method compatible with the
    expectations of BatchApiClient but delegates actual HTTP work to a
    `requests.Session`.
    """

    def __init__(self, base_url: str, verify: bool = True) -> None:
        self._session = requests.Session()
        self._session.verify = verify
        self._base_url = base_url.rstrip("/")

    def post(
        self,
        url: str,
        data: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        catch_response: bool = False,  # noqa: ARG002
        name: Optional[str] = None,  # noqa: ARG002
        **kwargs: Any,
    ) -> RequestsResponseContext:
        return self.request(
            "post", url, data=data, headers=headers, catch_response=catch_response, name=name, **kwargs
        )

    def get(
        self,
        url: str,
        data: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        catch_response: bool = False,  # noqa: ARG002
        name: Optional[str] = None,  # noqa: ARG002
        **kwargs: Any,
    ) -> RequestsResponseContext:
        return self.request(
            "get", url, data=data, headers=headers, catch_response=catch_response, name=name, **kwargs
        )

    def put(
        self,
        url: str,
        data: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        catch_response: bool = False,  # noqa: ARG002
        name: Optional[str] = None,  # noqa: ARG002
        **kwargs: Any,
    ) -> RequestsResponseContext:
        return self.request(
            "put", url, data=data, headers=headers, catch_response=catch_response, name=name, **kwargs
        )

    def delete(
        self,
        url: str,
        data: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        catch_response: bool = False,  # noqa: ARG002
        name: Optional[str] = None,  # noqa: ARG002
        **kwargs: Any,
    ) -> RequestsResponseContext:
        return self.request(
            "delete", url, data=data, headers=headers, catch_response=catch_response, name=name, **kwargs
        )

    def request(
        self,
        method: str,
        url: str,
        data: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        catch_response: bool = False,  # noqa: ARG002 - kept for compatibility
        name: Optional[str] = None,  # noqa: ARG002 - kept for compatibility
        **kwargs: Any,
    ) -> RequestsResponseContext:
        if url.startswith("http://") or url.startswith("https://"):
            full_url = url
        else:
            full_url = f"{self._base_url}{url}"

        response = self._session.request(method, full_url, data=data, headers=headers, **kwargs)
        return RequestsResponseContext(response)


def _bool_from_env(name: str, default: str = "False") -> bool:
    value = os.environ.get(name, default)
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in ("true", "1", "yes", "y"):
            return True
        if lowered in ("false", "0", "no", "n"):
            return False
    return False


def obtain_token(base_url: str, key: str, secret: str, oauth_endpoint: str, verify: bool) -> str:
    if oauth_endpoint.startswith("http://") or oauth_endpoint.startswith("https://"):
        token_url = oauth_endpoint
    else:
        token_url = f"{base_url.rstrip('/')}{oauth_endpoint}"
    payload = {
        "client_id": key,
        "client_secret": secret,
        "grant_type": "client_credentials",
    }

    response = requests.post(token_url, data=payload, verify=verify)
    if response.status_code != 200:
        raise RuntimeError(
            f"Token request failed: {response.status_code} {response.text}"
        )

    body = json.loads(response.text)
    return body["access_token"]


def main() -> None:
    # Load environment variables from a .env file if present (e.g., at the
    # solution root), falling back to the process environment if not.
    load_dotenv(find_dotenv())

    # Normalize IGNORE_TLS_CERTIFICATE so that code paths using eval() on this
    # value (e.g., EdFiBasicAPIClient) receive a capitalized boolean token.
    raw_ignore = os.environ.get("IGNORE_TLS_CERTIFICATE")
    if raw_ignore is not None:
        if str(raw_ignore).strip().lower() in ("true", "1", "yes", "y"):
            os.environ["IGNORE_TLS_CERTIFICATE"] = "True"
        elif str(raw_ignore).strip().lower() in ("false", "0", "no", "n"):
            os.environ["IGNORE_TLS_CERTIFICATE"] = "False"

    base_url = os.environ.get("PERF_API_BASEURL")
    key = os.environ.get("PERF_API_KEY")
    secret = os.environ.get("PERF_API_SECRET")
    oauth_endpoint = os.environ.get("PERF_API_OAUTH_ENDPOINT", "/oauth/token")
    ignore_cert = _bool_from_env("IGNORE_TLS_CERTIFICATE", "False")

    if not base_url or not key or not secret:
        raise RuntimeError(
            "PERF_API_BASEURL, PERF_API_KEY, and PERF_API_SECRET must be set "
            "in the environment to run the student batch integration test."
        )

    verify = not ignore_cert

    token = obtain_token(base_url, key, secret, oauth_endpoint, verify)

    http_adapter = RequestsHttpSessionAdapter(base_url=base_url, verify=verify)

    # Make the generic EdFiAPIClient base aware of this HTTP client and token so
    # that any shared-resource helpers used by factories (e.g., SchoolClient)
    # can function correctly.
    from edfi_performance_test.api.client.ed_fi_api_client import EdFiAPIClient

    EdFiAPIClient.client = http_adapter
    EdFiAPIClient.token = token

    # Import the factory only after EdFiAPIClient is initialized, to avoid
    # errors from shared-resource helpers that run at import time.
    from edfi_performance_test.factories.resources.student import StudentFactory

    batch_client = BatchApiClient(client=http_adapter, base_url=base_url, token=token)

    # Build multiple logical student records and corresponding triples to
    # more closely mirror the batch volume behavior and expose any potential
    # identity-conflict issues when multiple creates are present in the same
    # batch.
    triple_count_env = os.environ.get("MANUAL_BATCH_TRIPLE_COUNT", "3")
    try:
        triple_count = int(triple_count_env)
    except ValueError:
        triple_count = 3

    operations = []
    for index in range(triple_count):
        document = StudentFactory.build_dict()
        natural_key = {"studentUniqueId": document["studentUniqueId"]}

        operations.append(
            {
                "op": "create",
                "resource": "students",
                "document": document,
            }
        )
        operations.append(
            {
                "op": "update",
                "resource": "students",
                "naturalKey": natural_key,
                "document": dict(document),
            }
        )
        operations.append(
            {
                "op": "delete",
                "resource": "students",
                "naturalKey": natural_key,
            }
        )

    print(
        f"Sending batch with {len(operations)} operations "
        f"({triple_count} student triples) to {base_url}/batch"
    )
    print("Batch operations payload:")
    print(json.dumps(operations, indent=2))
    result = batch_client.post_batch(
        operations, name=f"students-batch-{triple_count}"
    )

    print(f"Batch success: {result.success}")
    if result.success:
        for op in result.operations:
            print(
                f"  index={op.index}, status={op.status}, op={op.op}, "
                f"resource={op.resource}, documentId={op.documentId}"
            )
    else:
        if result.failed_operation is not None:
            problem = result.failed_operation.problem
            print("Batch failed operation:")
            print(f"  index={result.failed_operation.index}")
            print(f"  op={result.failed_operation.op}")
            print(f"  resource={result.failed_operation.resource}")
            print(f"  problem.status={problem.get('status')}")
            print(f"  problem.type={problem.get('type')}")
            print(f"  problem.detail={problem.get('detail')}")
        else:
            print("Batch failed without a parsed failedOperation payload.")


if __name__ == "__main__":
    main()
