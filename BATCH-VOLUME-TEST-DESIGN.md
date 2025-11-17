# Design: Dedicated Batch Volume Scenarios for DMS

## 1. Overview

The current performance harness (`src/edfi-performance-test`) was built around single-resource REST calls (`/data/...`) and assumes:

- Each `POST`/`PUT`/`DELETE` is executed immediately.
- Dependencies are created and torn down synchronously via `create_with_dependencies` / `delete_with_dependencies`.
- Tests reason about concrete `id` values and per-request failures.

These assumptions conflict with the transactional, deferred nature of the DMS `/batch` endpoint. Rather than trying to retrofit batching under the existing `EdFiAPIClient` and TaskSet abstractions, this design introduces **explicit, dedicated batch volume scenarios**:

- New Locust users and tasks that treat `/batch` as the primary operation.
- Explicit control over which resources and dependencies participate in each batch.
- Simple, local error handling per batch request.

Existing PIPECLEAN, VOLUME, and CHANGE_QUERY tests remain unchanged and continue to use single-resource endpoints.

## 2. Goals and Non‑Goals

### 2.1 Goals

- Measure throughput and latency of the DMS `/batch` endpoint under realistic load.
- Exercise typical volume patterns (create/update/delete) using batch semantics.
- Explicitly replicate the **external effect** of the existing VOLUME tests: a repeating series of `POST`/`PUT`/`DELETE` triples for a given resource, now delivered via `/batch` instead of three separate single-resource calls.
- Keep dependencies valid at the time of the batched operations (no unresolved references).
- Avoid touching existing clients/tasks, minimizing risk to current certification tests.
- Make failures in a batch visible and attributable in Locust statistics and logs.

### 2.2 Non‑Goals

- Do not change `EdFiAPIClient` behavior or existing volume/pipeclean scenarios.
- Do not attempt to transparently batch *all* existing traffic.
- Do not cover every Ed‑Fi resource; start with a tight set of representative, high‑traffic resources (e.g., Students, Sections).

## 3. Batch API Recap (DMS)

- Endpoint: `POST /batch`
- Request body: JSON array of operations:

  ```json
  {
    "op": "create" | "update" | "delete",
    "resource": "Student" | "Section" | ...,
    "document": { ... },        // create/update
    "documentId": "uuid",       // update/delete by id
    "naturalKey": { ... },      // update/delete by natural key
    "ifMatch": "etag"           // optional per-op optimistic concurrency
  }
  ```

- On success: HTTP 200 with per-operation results (including `documentId`).
- On failure: single 4xx/409/412 response with a `failedOperation` descriptor; entire transaction rolled back.

The batch tests will **not** attempt to cover the full flexibility of the API. They will focus on:

- `create` + `update` + `delete` flows for a small set of resources.
- Batches containing homogeneous operations (one primary resource type + optional supporting resources).

## 4. High‑Level Test Architecture

### 4.1 New Test Type

- Extend `TestType` in `helpers/test_type.py` with `BATCH_VOLUME`.
- Extend the CLI (`helpers/argparser.py`) to accept `--testType BATCH_VOLUME`.
- Add a new `run_batch_volume_tests` entry point in `performance_tester.py`:
  - Mirrors `run_volume_tests`, but wires a new Locust user class.

### 4.2 New Locust User and Task Base

Location: `edfi_performance_test/tasks/batch_volume/`

- `BatchVolumeTestUser(FastHttpUser)`
  - Responsible for:
    - Setting `host = baseUrl` (no `/data` suffix).
    - Initializing a shared OAuth token (reuse `EdFiBasicAPIClient.login` logic or the paging-test request client).
    - Loading any static fixtures (e.g., shared School, Course, etc.) used across batches.
  - Dynamically discovers batch volume task classes under `tasks.batch_volume` similarly to `VolumeTestUser`.

- `BatchVolumeTestBase(TaskSet)`
  - Provides:
    - A `BatchApiClient` instance (see below).
    - Convenience methods to build batch operations for a resource (`build_create_op`, `build_update_op`, `build_delete_op`).
    - A `run_scenario` task that:
      - Constructs a batch of `N` create/update/delete operations.
      - Submits the batch via client and validates the response.
      - Marks the Locust request as success/failure accordingly.

### 4.3 BatchApiClient

Location: `edfi_performance_test/api/client/batch_api_client.py`

Responsibilities:

- Wrap `locust.clients.HttpSession`:
  - `post_batch(operations: List[Dict]) -> BatchResult`
  - Handles:
    - Setting `Authorization` header.
    - URL construction: `"{baseUrl}/batch"`.
    - Basic retry on transient network errors (optional).
- Parse the `/batch` response:
  - On HTTP 200:
    - Return a `BatchResult` with per-operation status and `documentId`.
  - On 4xx/409/412:
    - Return a `BatchResult` that encapsulates `failedOperation` details.
  - On 5xx:
    - Signal error up to Locust so the request is marked failed.

`BatchResult` can be a simple dataclass:

- `success: bool`
- `operations: List[OperationOutcome]` on success.
- `failed_operation: Optional[FailedOperation]` on failure.

### 4.4 Factories and Payloads

We reuse existing factories for building resource documents:

- `SchoolFactory`, `StudentFactory`, `SectionFactory`, etc. (`edfi_performance_test/factories/resources/`).
- For each batch scenario:
  - Use the factory to build the `document` payload (dict).
  - For updates:
    - Clone the factory output and tweak the attribute under test.
  - For deletes:
    - Use either:
      - The `documentId` returned in the batch success results, or
      - The natural key (using the same identity fields as the resource metadata).

No changes to existing factories are needed; batch scenarios work at the dict level they already produce.

## 5. Batch Volume Scenarios

### 5.1 Scenario Structure

For each primary resource (e.g., `Student`, `Section`), define a task class under `tasks.batch_volume`:

- Example: `StudentBatchVolumeTest(BatchVolumeTestBase)`
  - `resource = "Student"`
  - `factory = StudentFactory`
  - `dependencies`: e.g., pre-created `School` IDs or `StudentSchoolAssociation` operations.

Each scenario:

1. Builds `T` triples (create+update+delete) in memory:
   - For each triple:
     - `create` operation:
       - `op: "create"`
       - `resource: "Student"`
       - `document: <factory-generated dict>`
     - `update` operation:
       - `op: "update"`
       - `resource: "Student"`
       - `naturalKey` or `documentId` from the create.
       - `document` with a modified attribute.
     - `delete` operation:
       - `op: "delete"`
       - `documentId` or `naturalKey` matching the created student.
2. Optionally inject supporting operations (e.g., create a `StudentSchoolAssociation` and later delete it) in the same batch.
3. Submits all operations in a single `/batch` request using `BatchApiClient`.
4. Marks the Locust HTTP request as success if:
   - HTTP 200 AND all operation outcomes indicate success.
5. Marks as failure otherwise, logging the `failedOperation` details for analysis.

### 5.2 Dependency Management Strategy

To avoid unresolved-reference errors:

- **Option A: Fixture-First Approach (initial implementation)**
  - Use existing single-resource clients before the test run to create shared fixture resources:
    - e.g., one or more `School` and `CourseOffering` instances.
  - Store their natural keys (not IDs) and reference them from batch documents.
  - Do not delete fixture resources inside batch scenarios; treat them as quasi-permanent for the duration of the test.

- **Option B: Full In-Batch Dependencies (advanced)**
  - Within a single batch:
    - First `create` the dependency resource (e.g., `CourseOffering`).
    - Then `create` the primary resource (`Section`) referencing it by natural key.
  - Only adopt this once the basic fixture-first scenarios are stable; it requires more careful ordering and identity resolution.

Initial design will implement **Option A**, which is simpler and robust.

### 5.3 Representative Scenarios

Start with:

- `StudentBatchVolumeTest`
  - Uses shared `School` fixture for references.
  - Triples: create/update/delete `Student` only.
- `SectionBatchVolumeTest`
  - Uses shared `School` and `CourseOffering` fixtures.
  - Triples: create/update/delete `Section`.
- Optional: `StudentSchoolAssociationBatchVolumeTest`
  - Uses shared `Student` and `School` fixtures.
  - Triples: create/update/delete association.

## 6. Locust Integration and Metrics

### 6.1 User Lifecycle and Concurrency

`BatchVolumeTestUser` should mirror the existing `VolumeTestUser`:

- `clientCount`, `spawnRate`, and `runTimeInMinutes` are reused.
- Each user runs several batch scenarios (task classes) in round-robin or random order.

Because each `/batch` request represents many operations, throughput metrics must be interpreted as:

- Requests/sec (batches) vs.
- Operations/sec (batches * operations per batch).

### 6.2 Naming and Stats

To keep Locust statistics readable:

- Name the batch request `{resource}-batch-{tripleCount}`, e.g., `students-batch-10`.
- Include the number of operations in the log message (`len(operations)`).

This allows easy comparison between legacy volume tests and batch volume tests.

## 7. Error Handling Strategy

- On HTTP 200:
  - Inspect each per-operation result.
  - If any indicates failure, mark the Locust request as failed and log the corresponding operation index and problem details.
- On HTTP 4xx/409/412:
  - Parse the `failedOperation` payload.
  - Log:
    - `failedOperation.index`
    - `failedOperation.op`
    - `failedOperation.resource`
    - Problem type/title/status.
  - Mark Locust request as failed.
- On HTTP 5xx or network error:
  - Optional single retry (for transient issues).
  - If still failing, mark Locust request as failed.

No retry logic is attempted for semantic errors (validation, unresolved references, etc.).

## 8. CLI, Config, and Discovery

- CLI:
  - `--testType BATCH_VOLUME` dispatches to `run_batch_volume_tests`.
  - Reuse existing flags for runtime, client count, logging, etc.
  - Batch-size per request is controlled by a new `--batchTripleCount` (or reusing the existing flag name if already present).
- Config:
  - DMS discovery (base metadata + OpenAPI) is used *only* if needed to derive identity/natural key fields.
  - Otherwise, batch scenarios rely on known natural keys from the factories.

## 9. Implementation Plan

1. **Scaffolding**
   - Add `BATCH_VOLUME` to `TestType`.
   - Update `argparser` and `performance_tester` with `run_batch_volume_tests`.
   - Create `BatchApiClient` and `BatchVolumeTestUser` skeletons.
2. **Base Scenario**
   - Implement `BatchVolumeTestBase` with shared helpers.
   - Implement `StudentBatchVolumeTest` as the first scenario.
   - Add one or two fixtures for `School`.
3. **Validation**
   - Manually exercise a single user in debug mode against a local DMS instance.
   - Confirm:
     - Per-batch success.
     - Correct handling of failures.
     - No unresolved-reference errors (fixture-first strategy).
4. **Additional Scenarios**
   - Add `SectionBatchVolumeTest` and others as needed.
5. **Documentation**
   - Update `README.md` to describe BATCH_VOLUME usage and how to interpret batch metrics.

This approach keeps batching localized to a dedicated set of tests, avoids altering the existing certification harness, and aligns more naturally with the semantics and constraints of the DMS `/batch` endpoint.*** End Patch```} ***!
