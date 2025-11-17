[ ] **Section 1: Core Plumbing and Test Type**

- [ ] Define new `BATCH_VOLUME` enum value in `helpers/test_type.py`.
- [ ] Extend CLI parsing in `helpers/argparser.py` to accept `--testType BATCH_VOLUME`.
- [ ] Update `helpers/main_arguments.py` and any consumers to ensure `TestType.BATCH_VOLUME` flows through without special casing.
- [ ] Add a new `run_batch_volume_tests(args: MainArguments)` function in `performance_tester.py` modeled after `run_volume_tests`.
- [ ] Wire `run(args)` in `performance_tester.py` to dispatch to `run_batch_volume_tests` when `args.testType == TestType.BATCH_VOLUME`.

[ ] **Section 2: Batch API Client**

- [ ] Create `edfi_performance_test/api/client/batch_api_client.py`.
- [ ] Implement `BatchApiClient` wrapping `locust.clients.HttpSession`:
  - [ ] Constructor accepting `HttpSession`, `base_url`, and `token`.
  - [ ] `post_batch(operations: List[Dict[str, Any]]) -> BatchResult` method that:
    - [ ] Builds the `/batch` URL from the `base_url`.
    - [ ] Sends the JSON array using the Locust client (`catch_response=True`).
    - [ ] Applies `Authorization` and `Content-Type: application/json` headers.
- [ ] Define `BatchResult` and supporting dataclasses:
  - [ ] `OperationOutcome` for per-operation success metadata (`index`, `op`, `resource`, `documentId`, etc.).
  - [ ] `FailedOperation` reflecting DMS `failedOperation` shape.
  - [ ] `BatchResult` with `success`, `operations`, and `failed_operation`.
- [ ] Implement response parsing:
  - [ ] On HTTP 200, parse array of operation results into `BatchResult.success == True`.
  - [ ] On HTTP 4xx/409/412 with `failedOperation`, parse into `BatchResult.success == False` and populate `failed_operation`.
  - [ ] On HTTP 5xx or network error, mark Locust response as failure and raise or return an error-state `BatchResult`.
- [ ] Add minimal unit tests for `BatchApiClient` using a fake `HttpSession` or monkeypatched Locust client to validate:
  - [ ] Payload serialization.
  - [ ] Success path parsing.
  - [ ] Failure path parsing (including `failedOperation`).

[ ] **Section 3: Batch Volume User and Base Task**

- [ ] Create a new package `edfi_performance_test/tasks/batch_volume/`.
- [ ] Implement `BatchVolumeTestBase(TaskSet)`:
  - [ ] Initialize a `BatchApiClient` instance using the Locust user’s HTTP client and the current OAuth token.
  - [ ] Provide helper methods:
    - [ ] `build_create_op(resource: str, document: Dict[str, Any]) -> Dict`.
    - [ ] `build_update_op(resource: str, document_id: str, document: Dict[str, Any]) -> Dict`.
    - [ ] `build_delete_op(resource: str, document_id: str) -> Dict`.
  - [ ] Implement a template method `run_triple_batch(self, resource: str, documents: List[Dict[str, Any]])` that:
    - [ ] Accepts a list of factory-generated documents (one per triple).
    - [ ] Builds the corresponding create/update/delete operations.
    - [ ] Submits them via `BatchApiClient.post_batch`.
    - [ ] Marks the Locust request as success/failure based on `BatchResult`.
- [ ] Implement `BatchVolumeTestUser(FastHttpUser)`:
  - [ ] Set `min_wait` / `max_wait` or tick rate analogous to `VolumeTestUser`.
  - [ ] In `on_start`:
    - [ ] Associate the Locust `self.client` with an OAuth token (either via `EdFiBasicAPIClient` or a small login helper).
    - [ ] Discover and import all batch volume scenarios under `tasks.batch_volume`, similar to `VolumeTestUser`’s dynamic loading.
  - [ ] Append discovered `BatchVolumeTestBase` subclasses to `self.tasks`.
- [ ] Wire `run_batch_volume_tests(args)` in `performance_tester.py` to:
  - [ ] Configure Locust `Environment` with `BatchVolumeTestUser`.
  - [ ] Use `clientCount`, `spawnRate`, and `runTimeInMinutes` from `args`.

[ ] **Section 4: Fixtures and Shared Dependencies**

- [ ] Decide on the fixture-first strategy for dependencies (Option A from the design).
- [ ] Implement a `batch_volume_fixtures.py` module:
  - [ ] Provide `get_or_create_shared_school() -> Dict` returning natural key(s) usable in batch documents.
  - [ ] Provide additional helpers as needed (e.g., `get_or_create_shared_course_offering()`).
- [ ] Use existing non-batch `EdFiAPIClient` subclasses inside the fixture module to:
  - [ ] Create the fixture resources once at startup if they do not exist.
  - [ ] Cache their natural keys (not just `id`) for reuse.
- [ ] Ensure fixture creation runs:
  - [ ] Either in `BatchVolumeTestUser.on_start` for the first user only (use a class-level flag for one-time initialization).
  - [ ] Or in a dedicated test harness step before starting Locust.

[ ] **Section 5: First Scenario – StudentBatchVolumeTest**

- [ ] Create `tasks/batch_volume/student_batch_volume.py`.
- [ ] Implement `StudentBatchVolumeTest(BatchVolumeTestBase)`:
  - [ ] Reference `StudentFactory` to build documents.
  - [ ] Use `get_or_create_shared_school()` to embed a valid `schoolReference` / `educationOrganizationReference` where required.
  - [ ] Expose a `@task` method (e.g., `run_student_batch`) that:
    - [ ] Builds `N` student payloads using `StudentFactory.build_dict`.
    - [ ] For each payload, clones and modifies one attribute for the update step.
    - [ ] Calls `run_triple_batch("Student", documents)`.
- [ ] Ensure the triple structure mirrors the existing volume test externally:
  - [ ] For each logical “record,” there is one create, one update, and one delete operation in the batch.
  - [ ] The overall operation count per batch equals `3 * batchTripleCount` for that scenario.
- [ ] Add a small integration-style test (not Locust-driven) that:
  - [ ] Constructs a `BatchApiClient` against a local or mocked DMS.
  - [ ] Submits a single triple for Student.
  - [ ] Verifies the success response and that a subsequent delete by `documentId` is valid.

[ ] **Section 6: Additional Scenario – SectionBatchVolumeTest**

- [ ] Create `tasks/batch_volume/section_batch_volume.py`.
- [ ] Implement `SectionBatchVolumeTest(BatchVolumeTestBase)`:
  - [ ] Reference `SectionFactory` for documents.
  - [ ] Use fixtures for `School` and `CourseOffering` to avoid unresolved references.
  - [ ] Build triples where:
    - [ ] The create references existing School and CourseOffering via natural keys.
    - [ ] The update modifies a non-identity attribute (e.g., `sequenceOfCourse`).
    - [ ] The delete removes the created Section by `documentId`.
- [ ] Exercise at least one scenario with mixed-resource batches:
  - [ ] Example: include both `CourseOffering` and `Section` operations in the same batch.
  - [ ] Ensure correct ordering in the operations array (dependencies before dependents).

[ ] **Section 7: Configuration, Metrics, and Tuning**

- [ ] Add a `--batchTripleCount` CLI option to control triples per batch if not already present, and reuse it in batch volume scenarios.
- [ ] Expose per-scenario configuration for batch size (e.g., allow overriding `batchTripleCount` per test via environment variable or class attribute).
- [ ] Ensure Locust request names clearly identify:
  - [ ] The resource (e.g., `students` vs. `sections`).
  - [ ] The batch size (triples per batch).
  - [ ] Example name: `students-batch-10`.
- [ ] Confirm CSV output and Locust web UI show:
  - [ ] Request counts in batches.
  - [ ] Latencies for the full batch.
- [ ] Document how to interpret operations/sec:
  - [ ] `ops/sec ≈ (requests/sec) * (triples per batch) * 3`.

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

