# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# See the LICENSE and NOTICES files in the project root for more information.

"""
Manual test: two Student creates in a single /batch request.

This script is intended to provide a minimal repro for DMS batch behavior when
multiple create operations for the same resource type are present in one batch.

It does NOT include update/delete operations; the batch consists purely of two
`op: "create"` Student operations, each with a distinct natural key
(`studentUniqueId`).

Usage example (from src/edfi-performance-test/):

    poetry run python -m edfi_performance_test.manual_student_double_create_batch

Environment variables:

    PERF_API_BASEURL          Base URL of the DMS instance (e.g., http://localhost:8080)
    PERF_API_KEY              OAuth client id
    PERF_API_SECRET           OAuth client secret
    PERF_API_OAUTH_ENDPOINT   OAuth path or full URL (default: /oauth/token)
    IGNORE_TLS_CERTIFICATE    True/False (default: False)
"""

import json
import os
from typing import Any, Dict, Optional

from dotenv import load_dotenv, find_dotenv

from edfi_performance_test.api.client.batch_api_client import BatchApiClient
from edfi_performance_test.manual_student_batch_integration import (
    RequestsHttpSessionAdapter,
    _bool_from_env,
    obtain_token,
)


def main() -> None:
    # Load .env if present, then fall back to existing environment variables.
    load_dotenv(find_dotenv())

    base_url = os.environ.get("PERF_API_BASEURL")
    key = os.environ.get("PERF_API_KEY")
    secret = os.environ.get("PERF_API_SECRET")
    oauth_endpoint = os.environ.get("PERF_API_OAUTH_ENDPOINT", "/oauth/token")
    # Normalize IGNORE_TLS_CERTIFICATE so that downstream code paths that use
    # eval() on this value (e.g., EdFiBasicAPIClient) receive a capitalized
    # boolean token ('True' or 'False').
    raw_ignore = os.environ.get("IGNORE_TLS_CERTIFICATE")
    if raw_ignore is not None:
        if str(raw_ignore).strip().lower() in ("true", "1", "yes", "y"):
            os.environ["IGNORE_TLS_CERTIFICATE"] = "True"
        elif str(raw_ignore).strip().lower() in ("false", "0", "no", "n"):
            os.environ["IGNORE_TLS_CERTIFICATE"] = "False"

    ignore_cert = _bool_from_env("IGNORE_TLS_CERTIFICATE", "False")

    if not base_url or not key or not secret:
        raise RuntimeError(
            "PERF_API_BASEURL, PERF_API_KEY, and PERF_API_SECRET must be set "
            "in the environment to run this student double-create batch test."
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

    # Build two distinct Student documents and corresponding create operations.
    operations = []
    documents = []
    for index in range(2):
        document: Dict[str, Any] = StudentFactory.build_dict()
        documents.append(document)
        student_unique_id = document.get("studentUniqueId", "<missing>")
        print(f"Preparing student {index} with studentUniqueId={student_unique_id}")

        operations.append(
            {
                "op": "create",
                "resource": "students",
                "document": document,
            }
        )

    print(
        f"Sending batch with {len(operations)} operations "
        f"(2 student creates) to {base_url}/batch"
    )
    print("Batch operations payload:")
    print(json.dumps(operations, indent=2))

    result = batch_client.post_batch(operations, name="students-double-create-2")

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
