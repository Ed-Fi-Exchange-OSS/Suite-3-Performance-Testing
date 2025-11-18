# Running Volume Performance Tests

## Test environment

Docker is not being used. DMS, CMS and PostgreSQL are all running locally.

## Command to Run Tests

From `src/edfi-performance-test/`:

```bash
poetry run python -m edfi_performance_test \
  --runTimeInMinutes <MINUTES> \
  --output <OUTPUT_PATH> \
  --testType volume
```

Example:
```bash
cd src/edfi-performance-test
poetry run python -m edfi_performance_test \
  --runTimeInMinutes 10 \
  --output ../../DmsTestResults/test-run-name \
  --testType volume
```

## Running Batch Volume Tests (BATCH_VOLUME)

The batch volume tests exercise the DMS `/batch` endpoint instead of the single-resource `/data/...` endpoints. They send create/update/delete triples for supported resources (currently students and sections) as a single transactional batch.

### Basic Batch Volume Run

From `src/edfi-performance-test/`:

```bash
poetry run python -m edfi_performance_test \
  --runTimeInMinutes <MINUTES> \
  --output <OUTPUT_PATH> \
  --testType BATCH_VOLUME \
  --batchTripleCount 10
```

Notes:
- `--testType BATCH_VOLUME` enables the dedicated batch scenarios.
- `--batchTripleCount` (or `PERF_BATCH_TRIPLE_COUNT`) controls how many logical triples (create/update/delete) are included per batch for each scenario that uses `run_triple_batch`:
  - Example: `batchTripleCount=10` → 30 operations per batch request.
- The request names in Locust/CSV output follow the pattern:
  - `students-batch-10`, `sections-batch-10`, `mixed-students-sections-batch-2`, etc.
  - Each such request represents **one batch**.

Example:

```bash
cd src/edfi-performance-test
poetry run python -m edfi_performance_test \
  --runTimeInMinutes 10 \
  --output ../../DmsTestResults/batch-run-name \
  --testType BATCH_VOLUME \
  --batchTripleCount 10
```

### Single-User Debug Sessions (BATCH_VOLUME)

For quick validation against a running DMS instance, you can run single-user debug sessions with specific batch scenarios:

#### Students only

```bash
cd src/edfi-performance-test
poetry run python edfi_performance_test \
  -t BATCH_VOLUME \
  -g \
  -tl StudentBatchVolumeTest \
  --batchTripleCount 2
```

#### Sections only

```bash
cd src/edfi-performance-test
poetry run python edfi_performance_test \
  -t BATCH_VOLUME \
  -g \
  -tl SectionBatchVolumeTest \
  --batchTripleCount 2
```

#### Mixed students + sections

```bash
cd src/edfi-performance-test
poetry run python edfi_performance_test \
  -t BATCH_VOLUME \
  -g \
  -tl MixedStudentSectionBatchVolumeTest \
  --batchTripleCount 1
```

In each case:
- `-g` (`--runInDebugMode`) uses Locust single-user mode.
- `-tl` restricts execution to the specified batch task.
- `--batchTripleCount` keeps each batch small for easier debugging.

### Interpreting Batch Results

For BATCH_VOLUME runs:

- Each request name (e.g., `students-batch-10`) in the Locust CSVs corresponds to one batch request.
- The number of operations per batch is approximately `triples per batch * 3` for simple scenarios.
- The `extract-metrics.js` script will, when `PERF_TEST_TYPE=batch_volume` and `PERF_BATCH_TRIPLE_COUNT` are set, compute and print an additional **BATCH VOLUME** section:
  - Triples per batch
  - Requests/sec (batches per second)
  - Operations/sec (effective logical operations per second)
```

## Expected Behavior

### Normal Startup
- Test prints "Starting performance test..."
- Spawns N users (default 10)
- Runs for specified duration
- Prints "Finished running performance tests in X seconds"
- Exits with code 0

### Expected Warnings (Non-Fatal)
The test will log many ERROR messages about "There no local education agencies". These are SAFE TO IGNORE:
- Certain test factories fail to initialize due to missing LEA data
- These errors are non-fatal - the test continues successfully
- Thousands of requests will still execute successfully
- Check output files to verify test is working

### Authorization Errors
If you get invalid client credentials or other authentication errors, read the /home/brad/work/dms-root/Data-Management-Service/dataload-creds.json file and update the key and secret in the /home/brad/work/dms-root/Suite-3-Performance-Testing/.env file with the key and secret from dataload-creds.json

### Test Duration
Tests run in background for specified time (5-30+ minutes). The process will exit automatically when complete.

## Output Files

Four files created in output directory:

1. `volume_stats.csv` - Final aggregated statistics per endpoint
2. `volume_stats_history.csv` - Time-series data throughout test run
3. `volume_exceptions.csv` - Logged exceptions (includes LEA warnings)
4. `volume_failures.csv` - Failed requests (should be minimal/empty)

## Analyzing Results

### Key Metrics in volume_stats.csv

Last line (Aggregated row) contains overall statistics:

```csv
Type,Name,Request Count,Failure Count,Median Response Time,Average Response Time,Min,Max,Avg Content Size,Requests/s,Failures/s,50%,66%,75%,80%,90%,95%,98%,99%,99.9%,99.99%,100%
,Aggregated,26502,0,6,28.3,2,643,0.57,44.24,0.0,6,7,8,8,9,360,420,430,440,470,640
```

Column index:
- Column 3: Total Request Count
- Column 4: Failure Count (should be 0 or very low)
- Column 5: Median Response Time (ms)
- Column 6: Average Response Time (ms)
- Column 10: Requests per second (throughput)
- Column 16: 95th percentile response time
- Column 17: 99th percentile response time

### Performance Benchmarks

Typical good performance (10 users, 10 minutes):
- Median: 5-10ms
- 95th percentile: <100ms
- 99th percentile: <500ms
- Throughput: 40-60 req/s
- Total requests: 20,000-35,000
- Failure count: 0

### Finding Slow Endpoints

Sort by median response time:
```bash
sort -t',' -k5 -n volume_stats.csv | tail -10
```

Common slow endpoints:
- `GET /data/ed-fi/localEducationAgencies` - 300-400ms (database query)
- `POST /data/ed-fi/schools` - May be slower due to complexity

## Recommended Metrics to Summarize

For summarizing response times, use:
1. **Median (50th percentile)** - Typical user experience
2. **95th percentile** - SLA standard
3. **99th percentile** - Tail latency
4. **Max** - Worst case
5. **Request count** - Statistical significance
6. **Requests/second** - Throughput
7. **Failure rate** - Reliability

Avoid using average alone as it's skewed by outliers.
