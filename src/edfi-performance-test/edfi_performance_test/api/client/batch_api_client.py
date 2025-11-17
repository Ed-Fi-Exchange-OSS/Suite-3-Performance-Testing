# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# See the LICENSE and NOTICES files in the project root for more information.

import json
import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from locust.clients import HttpSession
from requests import Response


logger = logging.getLogger("locust.runners")


@dataclass
class OperationOutcome:
    index: int
    status: str
    op: str
    resource: str
    documentId: Optional[str] = None
    raw: Optional[Dict[str, Any]] = None


@dataclass
class FailedOperation:
    index: int
    op: str
    resource: str
    problem: Dict[str, Any]


@dataclass
class BatchResult:
    success: bool
    operations: List[OperationOutcome]
    failed_operation: Optional[FailedOperation] = None


class BatchApiClient:
    """
    Lightweight client for the DMS /batch endpoint using a Locust HttpSession.

    This client is intentionally narrow in scope: it sends a JSON array of
    operations and parses the success or failure response into a BatchResult.
    """

    def __init__(self, client: HttpSession, base_url: str, token: str) -> None:
        self._client = client
        self._base_url = base_url.rstrip("/")
        self._token = token

    def _batch_url(self) -> str:
        return f"{self._base_url}/batch"

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self._token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    def post_batch(self, operations: List[Dict[str, Any]], name: Optional[str] = None) -> BatchResult:
        """
        Send a batch of operations to the DMS /batch endpoint.

        The Locust request is marked as success or failure based on HTTP status
        and body content. The parsed response is returned as a BatchResult.
        """

        url = self._batch_url()
        payload = json.dumps(operations)
        request_name = name or "batch"

        try:
            response = self._send_request(url, payload, request_name)
        except Exception as ex:  # pragma: no cover - defensive logging
            logger.error("Error sending batch request: %s", ex)
            # Represent a hard failure as an unsuccessful BatchResult with no operations.
            return BatchResult(success=False, operations=[], failed_operation=None)

        return self._parse_response(response)

    def _send_request(self, url: str, payload: str, name: str) -> Response:
        with self._client.request(
            "post",
            url,
            data=payload,
            headers=self._headers(),
            catch_response=True,
            name=name,
        ) as response:
            # Mark obvious server errors as failures so they show up in Locust stats.
            if response.status_code >= 500:
                response.failure(
                    f"Status code {response.status_code} is a failure for batch request"
                )
            return response  # type: ignore[return-value]

    @staticmethod
    def _parse_success_body(body: str) -> List[OperationOutcome]:
        try:
            items = json.loads(body)
        except json.JSONDecodeError:
            logger.error("Unable to parse batch success response as JSON: %s", body)
            return []

        outcomes: List[OperationOutcome] = []
        if not isinstance(items, list):
            logger.error("Expected list in batch success response but got: %s", type(items))
            return outcomes

        for item in items:
            if not isinstance(item, dict):
                continue
            outcomes.append(
                OperationOutcome(
                    index=item.get("index", -1),
                    status=item.get("status", ""),
                    op=item.get("op", ""),
                    resource=item.get("resource", ""),
                    documentId=item.get("documentId"),
                    raw=item,
                )
            )

        return outcomes

    @staticmethod
    def _parse_failed_operation(body: str) -> Optional[FailedOperation]:
        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            logger.error("Unable to parse batch error response as JSON: %s", body)
            return None

        failed = payload.get("failedOperation")
        if not isinstance(failed, dict):
            logger.error("Batch error response missing 'failedOperation': %s", body)
            return None

        problem = failed.get("problem")
        if not isinstance(problem, dict):
            problem = {}

        return FailedOperation(
            index=failed.get("index", -1),
            op=failed.get("op", ""),
            resource=failed.get("resource", ""),
            problem=problem,
        )

    def _parse_response(self, response: Response) -> BatchResult:
        if 200 <= response.status_code < 300:
            operations = self._parse_success_body(response.text)
            return BatchResult(success=True, operations=operations)

        if response.status_code in (400, 401, 403, 404, 409, 412, 413):
            failed_operation = self._parse_failed_operation(response.text)
            if failed_operation is None:
                # Treat as a generic failure if we cannot parse failedOperation.
                logger.error(
                    "Batch request failed with status %s but could not parse failedOperation.",
                    response.status_code,
                )
            # Ensure the Locust request is marked as failed so metrics reflect the error.
            try:
                response.failure(
                    f"Batch request failed with status {response.status_code}"
                )
            except Exception:
                # If response is already closed or cannot be marked, swallow the error.
                pass
            return BatchResult(success=False, operations=[], failed_operation=failed_operation)

        # For any other status codes (including 5xx), treat as server error.
        logger.error(
            "Unexpected status code from batch request: %s, body: %s",
            response.status_code,
            response.text,
        )
        try:
            response.failure(
                f"Batch request received unexpected status code {response.status_code}"
            )
        except Exception:
            pass
        return BatchResult(success=False, operations=[], failed_operation=None)

