# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# See the LICENSE and NOTICES files in the project root for more information.

import json
from types import SimpleNamespace
from typing import Any, Dict, List

import pytest

from edfi_performance_test.api.client.batch_api_client import (
    BatchApiClient,
    BatchResult,
    FailedOperation,
    OperationOutcome,
)


class FakeResponse:
    def __init__(self, status_code: int, text: str = "") -> None:
        self.status_code = status_code
        self.text = text
        self._failed = False
        self.request = SimpleNamespace(method="POST", url="http://test/batch")

    def failure(self, _message: str) -> None:
        self._failed = True

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        return None


class FakeHttpSession:
    def __init__(self, response: FakeResponse) -> None:
        self._response = response
        self.last_request_args: Dict[str, Any] = {}
        self.last_request_kwargs: Dict[str, Any] = {}

    def request(self, *args: Any, **kwargs: Any) -> FakeResponse:
        self.last_request_args = {"args": args}
        self.last_request_kwargs = kwargs
        return self._response


def _make_client(response: FakeResponse) -> BatchApiClient:
    session = FakeHttpSession(response)
    return BatchApiClient(client=session, base_url="http://test", token="token")


def test_post_batch_builds_url_and_headers() -> None:
    operations: List[Dict[str, Any]] = [{"op": "create", "resource": "students"}]
    response_body = json.dumps(
        [
            {
                "index": 0,
                "status": "success",
                "op": "create",
                "resource": "students",
                "documentId": "abc",
            }
        ]
    )
    fake_response = FakeResponse(status_code=200, text=response_body)
    session = FakeHttpSession(fake_response)

    client = BatchApiClient(client=session, base_url="http://test/", token="token123")

    result = client.post_batch(operations, name="students-batch-1")

    assert isinstance(result, BatchResult)
    assert result.success is True
    assert len(result.operations) == 1
    op_outcome: OperationOutcome = result.operations[0]
    assert op_outcome.resource == "students"
    # Verify URL and headers on the outgoing request
    assert session.last_request_args["args"][0] == "post"
    assert session.last_request_args["args"][1] == "http://test/batch"
    headers = session.last_request_kwargs.get("headers", {})
    assert headers.get("Authorization") == "Bearer token123"
    assert headers.get("Content-Type") == "application/json"


def test_post_batch_parses_failed_operation() -> None:
    error_payload = {
        "detail": "Batch operation failed and was rolled back.",
        "failedOperation": {
            "index": 1,
            "op": "create",
            "resource": "students",
            "problem": {
                "detail": "Data validation failed.",
                "status": 400,
            },
        },
    }
    fake_response = FakeResponse(status_code=400, text=json.dumps(error_payload))
    client = _make_client(fake_response)

    result = client.post_batch([{"op": "create", "resource": "students"}])

    assert result.success is False
    assert result.operations == []
    assert isinstance(result.failed_operation, FailedOperation)
    assert result.failed_operation.index == 1
    assert result.failed_operation.op == "create"
    assert result.failed_operation.resource == "students"
    assert result.failed_operation.problem["detail"] == "Data validation failed."


def test_post_batch_handles_server_error() -> None:
    fake_response = FakeResponse(status_code=500, text="internal error")
    client = _make_client(fake_response)

    result = client.post_batch([{"op": "create", "resource": "students"}])

    assert result.success is False
    assert isinstance(result, BatchResult)
    assert result.operations == []
    assert result.failed_operation is None

