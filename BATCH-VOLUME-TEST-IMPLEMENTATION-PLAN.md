[X] **Section 1: Core Plumbing and Test Type**

- [X] Define new `BATCH_VOLUME` enum value in `helpers/test_type.py`.
- [X] Extend CLI parsing in `helpers/argparser.py` to accept `--testType BATCH_VOLUME`.
- [X] Update `helpers/main_arguments.py` and any consumers to ensure `TestType.BATCH_VOLUME` flows through without special casing.
- [X] Add a new `run_batch_volume_tests(args: MainArguments)` function in `performance_tester.py` modeled after `run_volume_tests`.
- [X] Wire `run(args)` in `performance_tester.py` to dispatch to `run_batch_volume_tests` when `args.testType == TestType.BATCH_VOLUME`.
- [X] Confirm that batch behavior is only enabled via `--testType BATCH_VOLUME` (no generic `--useBatchEndpoint` toggle on other test types).

[X] **Section 2: Batch API Client**

- [X] Create `edfi_performance_test/api/client/batch_api_client.py`.
- [X] Implement `BatchApiClient` wrapping `locust.clients.HttpSession`:
  - [X] Constructor accepting `HttpSession`, `base_url`, and `token`.
  - [X] `post_batch(operations: List[Dict[str, Any]]) -> BatchResult` method that:
    - [X] Builds the `/batch` URL from the `base_url`.
    - [X] Sends the JSON array using the Locust client (`catch_response=True`).
    - [X] Applies `Authorization` and `Content-Type: application/json` headers.
- [X] Define `BatchResult` and supporting dataclasses:
  - [X] `OperationOutcome` for per-operation success metadata (`index`, `op`, `resource`, `documentId`, etc.).
  - [X] `FailedOperation` reflecting DMS `failedOperation` shape.
  - [X] `BatchResult` with `success`, `operations`, and `failed_operation`.
- [X] Implement response parsing:
  - [X] On HTTP 200, parse array of operation results into `BatchResult.success == True`.
  - [X] On HTTP 4xx/409/412 with `failedOperation`, parse into `BatchResult.success == False` and populate `failed_operation`.
  - [X] On HTTP 5xx or network error, mark Locust response as failure and raise or return an error-state `BatchResult`.
- [X] Add minimal unit tests for `BatchApiClient` using a fake `HttpSession` or monkeypatched Locust client to validate:
  - [X] Payload serialization.
  - [X] Success path parsing.
  - [X] Failure path parsing (including `failedOperation`).

[X] **Section 3: Batch Volume User and Base Task**

- [X] Create a new package `edfi_performance_test/tasks/batch_volume/`.
- [X] Implement `BatchVolumeTestBase(TaskSet)`:
  - [X] Initialize a `BatchApiClient` instance using the Locust user’s HTTP client and the current OAuth token.
  - [X] Define or reuse a convention so that each batch scenario provides the correct `resource` name for operations:
    - [X] `resource` must match the existing endpoint URL segment (e.g., `"students"`, `"sections"`, `"courses"`), aligned with `/data/{resource}` used by the single-resource APIs.
  - [X] Provide helper methods:
    - [X] `build_create_op(resource: str, document: Dict[str, Any]) -> Dict`.
    - [X] `build_update_op(resource: str, natural_key: Dict[str, Any], document: Dict[str, Any]) -> Dict`.
    - [X] `build_delete_op(resource: str, natural_key: Dict[str, Any]) -> Dict`.
  - [X] Implement a template method `run_triple_batch(self, resource: str, documents: List[Dict[str, Any]])` that:
    - [X] Accepts a list of factory-generated documents (one per triple).
    - [X] Derives the appropriate **natural key** structures from those documents via `get_natural_key`.
    - [X] Builds the corresponding create/update/delete operations:
      - [X] `create` with full document.
      - [X] `update` using the same natural key as the `create` to identify the record (with subclasses able to override `build_update_document`).
      - [X] `delete` using the same natural key.
    - [X] Treats these create+update+delete triples as a **no-concurrency scenario**:
      - [X] Does not attempt to fetch or manage per-operation ETags for in-batch updates.
      - [X] Relies on the backend’s batch implementation supporting this pattern.
    - [X] Submits them via `BatchApiClient.post_batch`.
    - [X] Relies on `BatchApiClient` to mark the Locust request as success/failure based on HTTP status and payload.
- [X] Implement `BatchVolumeTestUser(FastHttpUser)`:
  - [X] Set up OAuth for the user in `on_start` by associating `self.client` with an `EdFiBasicAPIClient` and storing the token on the user instance.
  - [X] In `on_start`:
    - [X] Discover and import all batch volume scenarios under `tasks.batch_volume`, similar to `VolumeTestUser`’s dynamic loading.
  - [X] Append discovered `BatchVolumeTestBase` subclasses to `self.tasks`.
- [X] Wire `run_batch_volume_tests(args)` in `performance_tester.py` to:
  - [X] Configure Locust `Environment` with `BatchVolumeTestUser`.
  - [X] Use `clientCount`, `spawnRate`, and `runTimeInMinutes` from `args`.
  - [X] Ensure that existing flags like `deleteResources` are effectively **ignored** by `BATCH_VOLUME` tests (which do not call single-resource delete methods) and only respected by legacy test types.

[X] **Section 4: Fixtures and Shared Dependencies**

- [X] Decide on the fixture-first strategy for dependencies (Option A from the design).
- [X] Implement a `batch_volume_fixtures.py` module:
  - [X] Provide `get_or_create_shared_school() -> Dict` returning natural key(s) usable in batch documents (e.g., `{"schoolId": <id>}`).
  - [X] Provide additional helpers as needed (e.g., `get_or_create_shared_course_offering()` returning course offering natural key fields).
- [X] Use existing non-batch `EdFiAPIClient` subclasses inside the fixture module to:
  - [X] Create the fixture resources once at startup if they do not exist (using `SchoolClient` and `CourseOfferingClient`).
  - [X] Cache their natural keys (not just `id`) for reuse via module-level variables and a threading lock.
- [X] Ensure fixture creation runs:
  - [X] In `BatchVolumeTestUser.on_start` so that shared fixtures are initialized once per test run and available to all batch volume scenarios.

[ ] **Section 5: First Scenario – StudentBatchVolumeTest**

[X] **Section 5: First Scenario – StudentBatchVolumeTest**

- [X] Create `tasks/batch_volume/student_batch_volume.py`.
- [X] Implement `StudentBatchVolumeTest(BatchVolumeTestBase)`:
  - [X] Reference `StudentFactory` to build documents.
  - [X] Use `get_or_create_shared_school()` to obtain a valid shared school natural key (for now, the natural key is available to scenarios; embedded references can be expanded as needed).
  - [X] Expose a `@task` method (`run_student_batch`) that:
    - [X] Builds `N` student payloads using `StudentFactory.build_dict` (`N` is `_batch_triple_count`).
    - [X] For each payload, clones and modifies one attribute for the update step via `build_update_document`.
    - [X] Derives the natural key structure required by the DMS batch API from each payload using `get_natural_key` (studentUniqueId).
    - [X] Calls `run_triple_batch("students", documents)`.
- [X] Ensure the triple structure mirrors the existing volume test externally:
  - [X] For each logical “record,” there is one create, one update, and one delete operation in the batch.
  - [X] The overall operation count per batch equals `3 * batchTripleCount` for that scenario.
- [X] Add a small integration-style test (not Locust-driven) that:
  - [X] Constructs a `BatchApiClient` against a running DMS using a lightweight HTTP adapter over the `requests` library (see `edfi_performance_test/manual_student_batch_integration.py`).
  - [X] Submits a single triple for Student (create/update/delete by natural key) to the `/batch` endpoint.
  - [X] Prints success/failure details and per-operation outcomes to the console for manual verification by the operator.

[X] **Section 6: Additional Scenario – SectionBatchVolumeTest**

- [X] Create `tasks/batch_volume/section_batch_volume.py`.
- [X] Implement `SectionBatchVolumeTest(BatchVolumeTestBase)`:
  - [X] Reference `SectionFactory` for documents.
  - [X] Use fixtures for `School`, `CourseOffering`, `ClassPeriod`, and `Location` to avoid unresolved references in section dependencies.
  - [X] Build triples where:
    - [X] The create references existing School and CourseOffering via natural keys (using `courseOfferingReference` fields).
    - [X] The create also references shared ClassPeriod and Location fixtures via their natural keys.
    - [X] The update modifies a non-identity attribute (e.g., `sequenceOfCourse`).
    - [X] The delete removes the created Section by matching natural key.

[X] **Section 6a: Mixed-Resource Batch Scenario (Students + Sections)**

- [X] Refactor `BatchVolumeTestBase` to expose a reusable helper for building triple operations without sending the batch:
  - [X] Add `build_triple_operations(self, resource: str, documents: List[Dict[str, Any]], get_natural_key=None, build_update_document=None) -> List[Dict[str, Any]]` that:
    - [X] For each document, derives the natural key via `get_natural_key` (defaulting to `self.get_natural_key`).
    - [X] Builds create/update/delete operations using `build_create_op`, `build_update_op`, and `build_delete_op`.
  - [X] Update `run_triple_batch` to call `build_triple_operations` and then send the resulting operations in a single `/batch` request.
- [X] Implement a new mixed-resource TaskSet, `MixedStudentSectionBatchVolumeTest(BatchVolumeTestBase)` in `tasks/batch_volume/mixed_student_section_batch_volume.py`:
  - [X] Use `StudentFactory` and `SectionFactory` to construct documents for student and section triples.
  - [X] In a `@task` method (`run_mixed_batch`):
    - [X] Build one student triple (1 student document → 3 operations) using `build_triple_operations` with student-specific natural key and update helpers.
    - [X] Build one section triple (1 section document → 3 operations), wiring the section document to existing fixtures (School, CourseOffering, ClassPeriod, Location) as in `SectionBatchVolumeTest`, and using section-specific natural key and update helpers.
    - [X] Concatenate the two sets of operations into a single array (6 operations total).
    - [X] Submit them via `BatchApiClient.post_batch` with a clear request name (e.g., `mixed-students-sections-batch-2`).
- [X] Ensure the mixed scenario:
  - [X] Still treats each triple as an independent logical record (no in-batch creation of dependencies that are referenced later in the same batch).
  - [X] Respects `MAX_BATCH_SIZE` by keeping the total operation count (`triples * 3`) within configured limits.
  - [X] Produces Locust stats where the mixed request name clearly indicates it is a mixed-resource batch.

[X] **Section 7: Configuration, Metrics, and Tuning**

- [X] Add a `--batchTripleCount` CLI option to control triples per batch if not already present, and reuse it in batch volume scenarios.
  - [X] Default this option to 10.
  - [X] Make it effective only when `--testType BATCH_VOLUME`; ignored by other test types (the argument and env var are global, but only `BatchVolumeTestBase` reads `PERF_BATCH_TRIPLE_COUNT`).
  - [X] Document that `3 * batchTripleCount` must not exceed the configured DMS `MAX_BATCH_SIZE` for the `/batch` endpoint (no runtime guard added yet; limit must be honored by configuration).
  - [X] Wire `--batchTripleCount` to the `PERF_BATCH_TRIPLE_COUNT` environment variable in `argparser.py` so it can be configured via env like other harness settings.q
- [X] Expose per-scenario configuration for batch size (e.g., allow overriding `batchTripleCount` per test via environment variable or class attribute).
- [X] Ensure Locust request names clearly identify:
  - [X] The resource (e.g., `students` vs. `sections`).
  - [X] The batch size (triples per batch) via the pattern `{resource}-batch-{tripleCount}`.
  - [X] Example name: `students-batch-10`.
- [X] Confirm CSV output and Locust web UI show:
  - [X] Request counts in batches (each request name represents one batch).
  - [X] Latencies for the full batch (per-request metrics inherently capture end-to-end batch latency).
- [X] Implement a small reporting helper (in the existing metrics extraction script) to compute and report an **operations/sec** metric for batch tests:
  - [X] Implemented in `extract-metrics.js`, extending the existing reporting for Locust CSVs.
  - [X] Uses the formula `ops/sec ≈ (requests/sec) * (triples per batch) * 3`, where `requests/sec` is derived from `Request Count` and `RUN_TIME_IN_MINUTES`.
  - [X] Only computes this when `PERF_TEST_TYPE` equals `batch_volume` and `PERF_BATCH_TRIPLE_COUNT` (or `BATCH_TRIPLE_COUNT`) is set; prints a `BATCH VOLUME` section with triples per batch, requests/sec, and operations/sec.

[ ] **Section 8: Validation and Rollout**

- [ ] Run a short, single-user debug session for `StudentBatchVolumeTest`:
  - [ ] Verify no unresolved-reference errors.
  - [ ] Confirm DMS logs show `/batch` usage with expected operation counts.
- [ ] Run a small multi-user batch volume test (e.g., 10 users for 5 minutes) to confirm:
  - [ ] Stable throughput.
  - [ ] Expected failure rates (ideally low for well-formed data).
  - [ ] Reasonable resource utilization on DMS.
- [ ] Compare results qualitatively to existing VOLUME tests:
  - [ ] Requests/sec vs. operations/sec.
  - [ ] Latency distribution per logical triple (inferred).
- [ ] Once stable, document usage in `README.md`:
  - [ ] CLI invocation examples for `BATCH_VOLUME`.
  - [ ] Notes on differences vs. legacy VOLUME tests.
  - [ ] Caveats (e.g., fixtures are not automatically cleaned up).
  - [ ] Include a note for contributors about running tests with `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` (e.g., `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 poetry run pytest`) to avoid interference from globally installed pytest plugins.
