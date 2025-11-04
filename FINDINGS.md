## Findings
- Load-test sessions repeatedly wait on `WALSync`/`WALWrite` during `COMMIT`, confirming insert/update/delete latency is dominated by WAL flushing instead of locks or CPU.
- `pg_stat_wal` shows ~667k `wal_write` = `wal_sync` events for ~1 GB of WAL, i.e., nearly every transaction forces its own fsync; the ingest pattern uses single-statement transactions with `synchronous_commit = on`.
- `dms.document` partitions carry large JSONB rows, are published with Debezium, and use `REPLICA IDENTITY FULL`, so updates/deletes log full row images and cascade via FK tables, inflating WAL volume.
- High churn continues to generate dead tuples on both `document_*` and `alias_*` partitions (~0.5M each); autovacuum is keeping up but will need tuning if delete sessions linger.

## Recommendations
- Batch writes per transaction or run the ingest sessions with `synchronous_commit = off` to reduce per-statement fsyncs and eliminate the `WALSync` stalls.
- Enable `track_io_timing` and `track_wal_io_timing` (plus `pg_stat_statements`) before the next run to capture detailed WAL/IO latency and per-query timings.
- If logical decoding is still required, switch `dms.document` partitions to `REPLICA IDENTITY USING INDEX`. If Debezium is no longer needed, drop the publication and revert to default replica identity to cut WAL size.
- Review Debezium setup: `wal_level` is `replica`; move to `logical` or disable replication features to match actual requirements.
- Lower table-specific `autovacuum_vacuum_scale_factor` for the large partitions so dead rows are reclaimed sooner, keeping WAL/checkpoint pressure in check.

## Update – 2025-10-26 (replication removed, authorization JSONB dropped)
- After removing logical replication artifacts (no publication/replica identity full) and the authorization JSONB columns, repeated sampling during the 12:03 CDT load-test window showed zero sustained `WALSync/WALWrite` waits; only a single transient wait appeared in 20 rapid checks.
- `pg_stat_wal` still records `wal_sync ≈ wal_write`, but NVMe fsync latency remained ≈0.13 ms and client backends no longer queue on commits; throughput is now limited by the synchronous single-statement transaction pattern rather than WAL contention.
- Dead tuple accumulation collapsed: document partitions now show ~5 k dead tuples each (down from ~50 k), and alias partitions ~3.9 k; autovacuum counts (6–7 per partition) indicate it is keeping pace post-change.
- WAL volume per 30 s interval is ~1.3 GB with `wal_buffers_full` no longer increasing, reflecting lighter row images without the dropped JSONB columns.

### Next Steps

  1. If ingest durability allows, batch multiple DML operations per transaction or run the loaders with SET synchronous_commit = OFF to cut fsyncs per second and create headroom.
  2. Before the next test, run SELECT pg_stat_reset_shared('wal'); (and pg_stat_reset();) so you get per-run WAL totals, and enable track_wal_io_timing = on/track_io_timing = on for direct flush
     timing.
  3. Keep an eye on row size: even after dropping authorization JSONB, WAL usage is ~184 KB per commit; if that’s higher than expected, consider compressing edfidoc (e.g., externalizing large
     blobs) or trimming unused attributes to keep WAL growth manageable.

    * jsonb values (like dms.document_00: edfidoc) are already TOASTed and compressed with the cluster’s default method (pglz). You can usually squeeze another 20‑40 % out of WAL and storage by
    switching the column to LZ4, because LZ4 compresses JSON better and also shrinks the undo/redo images written to WAL. Example:

    SHOW default_toast_compression;        -- confirm LZ4 is available
    ALTER TABLE dms.document ALTER COLUMN edfidoc SET COMPRESSION lz4;
    VACUUM (FULL, ANALYZE) dms.document;   -- optional, rewrites existing rows

    That change is transparent: every time PostgreSQL needs the value (including logical decoding for replication) it automatically TOAST-decompresses it before handing the plain JSON out, so
    downstream consumers still see the original document.
  - If the server was built without LZ4, you can still reduce WAL volume by raising ALTER TABLE … SET (toast_tuple_target = 2040); or by normalizing exceptionally large JSON fragments into child
    tables. Those approaches also keep the logical replication feed uncompressed.
  - Only when you need far stronger compression than LZ4 should you consider storing the payload as a compressed bytea yourself (e.g., pgp_sym_encrypt(lz4compress(edfidoc::text))). In that design
    you’d expose an updatable view or generated column that lz4decompresses back to jsonb for clients. Logical replication would publish whatever you store—so you’d add a decode step on the
    subscriber before handing it to downstream systems.

    Given your goal of re‑enabling replication and keeping downstream JSON untouched, the per-column LZ4 compression is the safest “flip the switch” option. After applying it, reset the WAL stats,
    rerun a load, and compare pg_stat_wal.wal_bytes and Debezium event size to ensure the trade-off meets your needs.

## Update – 2025-10-26 13:38 (replication removed, authorization JSONB dropped, config tuned)

• WAL & Commit Behavior

  - pg_stat_wal since 13:24:01 shows 1 216 691 records / 1.45 GB WAL with 81 303 fsyncs; average WAL write 0.033 ms and sync 0.379 ms (wal_write_time/wal_write, wal_sync_time/wal_sync), confirming
    each commit still forces an fsync but SSD latency stays sub‑millisecond.
  - Over 30 s windows the counters grow by ~3 900 fsyncs and ~120 MB WAL, matching ≈130 k inserts + 7 k updates + 22 k deletes per half minute (pg_stat_database, pg_stat_all_tables), so commit rate
    remains the throughput limiter rather than contention.

  Wait Events & Concurrency

  - Spot checks no longer show queues on WALWrite/WALSync; occasional single backends appear momentarily, and pg_stat_activity now reports most backends in active DELETEs or idle/commit states with
    no long-lived waits. No deadlocks or idle-in-transaction sessions.

  IO & Checkpoints

  - pg_stat_io indicates checkpointer handling ~10 M shared-buffer writes with total write_time 2404 ms and fsync_time 252 ms (avg ≈0.025 ms per flush), and pg_stat_bgwriter since 13:24 reports
    five timed checkpoints with minimal sync time (52 ms). No wal_buffers_full events and wal_buffers=2048 remains adequate.
  - iostat during the run shows ~200–280 WAL writes/sec at ~2 MB/s, queue depth <0.1, wait ~0.13 ms, so storage has plenty of headroom.

  Table Churn & Vacuum

  - Document partitions now accumulate ~4–5 k dead tuples each (total 46 k) and alias partitions ~36 k; autovacuum counts keep pace. Relation sizes are edging up (~1.86 GB per hot partition) due to
    ongoing churn rather than bloat explosion.

  Recommendations

  1. If ingest durability allows, batch multiple DMLs per transaction or use synchronous_commit = off for loaders to cut 80 k fsyncs/run; WAL timings show the device is keeping up now, but this
     remains the dominant cost and will scale linearly with load.
  2. Leave track_io_timing/track_wal_io_timing on—now you can monitor wal_sync_time deltas per test; continue resetting stats (pg_stat_reset_shared('wal'), pg_stat_reset()) at each run for clean
     baselines.
  3. Monitor dead tuple totals; current levels are small, but if they grow beyond a few hundred thousand, lower the autovacuum scale_factor on the hottest partitions to prevent JSONB heap expansion
     and extra WAL churn.

  No new bottlenecks emerged in this run; WAL durability cost is quantified and within device capability, so future tuning should target reducing commit frequency or payload size rather than
  PostgreSQL internals.

  ## Update - 2025-10-26 15:39 (replication removed, authorization JSONB dropped, config tuned, npgsql fixed)

• WAL & I/O

  - pg_stat_wal (reset 15:42:59) shows wal_sync_time 22.44 s across 59 617 syncs → ~0.38 ms per flush; wal_write_time 1.63 s across 59 626 writes → ~0.03 ms each, so WAL flushing is no longer a
    latency source.
  - Disk waits remain tiny: iostat -xd -p nvme1n1 1 6 reported w_await ≈0.15 ms, confirming the NVMe device is coasting.
  - Checkpoints are leisurely (3 timed checkpoints taking 539 s total) and there are no wal_buffers_full, indicating comfortable WAL headroom after your batching/config changes.

  Primary Bottleneck

  - CPU is dominated by PostgreSQL backends (10 workers at ~100 % each per top) executing DELETE FROM dms.Document … cascades.
  - EXPLAIN (ANALYZE, BUFFERS) on a representative delete completed in 189 ms, with 182 ms of that consumed by the cascade trigger alias_documentpartitionkey_documentid_fkey.
  - Drilling into dms.alias reveals the cause: the table partitions on referentialpartitionkey and no longer has indexes on (documentpartitionkey, documentid). As shown by EXPLAIN (ANALYZE) on
    DELETE FROM dms.alias …, PostgreSQL now performs sequential scans of all 16 partitions (≈470 k rows each) just to remove a single alias row, costing ~215 ms and 36 k buffer hits per delete.
  - Every document delete therefore forces 16 large scans plus the associated trigger work on dependent tables, which explains both the high CPU utilization and the remaining 150–200 ms
    response times for write operations.

  Application Layer

  - The DMS service (EdFi.DataManage…) is modest: pidstat shows it using ~33 % of a single CPU with zero wait time, so the app tier is not the limiting factor right now. Request latency is
    being dictated by the database-side cascades.

  Action Items

  1. Recreate an index that matches the FK lookup, e.g. CREATE INDEX CONCURRENTLY ON dms.alias (documentpartitionkey, documentid); (or define it on the partitioned parent so child partitions
     inherit it). Without it, every delete/update that touches the FK will keep scanning all partitions.
  2. Revisit partitioning for dms.alias: if most operations key on documentpartitionkey, align the partition key (or use sub-partitioning) so deletes hit a single partition and benefit from
     partition pruning.
  3. Audit other FK relationships from dms.document where the referencing table lost its supporting indexes during the schema cleanup; run EXPLAIN (ANALYZE) on their delete/update paths to
     ensure they’re using index scans.
  4. Keep track_wal_io_timing enabled and continue collecting short deltas (as you did) to validate WAL stays sub-millisecond after the schema/index fixes.
  5. Once the FK/index issue is resolved, rerun the load test and monitor pg_stat_activity for residual waits plus pg_stat_wal/pg_stat_database deltas to confirm that CPU usage and response
     times drop; only if latency persists should you revisit DMS-side batching/concurrency.

  These steps should eliminate the heavy cascade scans, letting the already-improved WAL behavior translate into better overall write latency.

   ## Update - 2025-10-16 26:41 (replication removed, authorization JSONB dropped, config tuned, npgsql fixed, Alias index added)

• Index Impact

  - The new FK index is being used on every alias partition; pg_stat_user_indexes shows alias_03_documentpartitionkey_documentid_idx and peers with idx_scan = 519 693 each.
  - EXPLAIN (ANALYZE) confirms deletes now hit the index: DELETE FROM dms.alias … completes in 0.38 ms, touching 42 buffers, versus the previous 215 ms full scans.
  - Cascading deletes now finish almost instantly (dms.document delete executes in 0.085 ms), so the previous CPU saturation on WAL + trigger cleanup is gone.

  Current Postgres Health

  - Load-test snapshot (16:41:33 reset): pg_stat_wal grew by ~0.77 GB in 30 s, with wal_sync +46 865 and wal_sync_time +15.5 s → average 0.33 ms per flush. wal_write_time only +0.69 s, so disk
    I/O isn’t throttling throughput.
  - Commit throughput is high: pg_stat_database climbed from 5 462 602 to 5 560 995 commits in 35 s (~2.8 k commits/s) with ~12 k deletes/s, showing the DB keeps pace with the workload.
  - Wait sampling now shows at most one backend at a time in WALSync/WALWrite, and that session often sits idle in transaction around a multi-statement CTE rather than blocking others.
  - Autovacuum remains healthy; alias/document partitions hold ≤11 k dead tuples with 8–10 autovac runs apiece, and pg_stat_bgwriter since reset shows only 4 checkpoints with moderate runtime.

  System View

  - Disk still has ample headroom: per iostat, w_await ≈0.11 ms while pushing 38–48 MB/s WAL traffic at ~3.4 k fsyncs/s (≈39 % util).
  - Postgres CPU usage dropped significantly; the top consumers are now the DMS loader and a Python client (top reports EdFi.DataManage at ~260–300 % CPU, while individual Postgres workers
    hover 30–40 %).
  - pidstat verifies the application process is the heaviest hitter (avg 284 % CPU, no wait), indicating remaining end-to-end response time issues are likely in the app layer or request
    orchestration, not the database.

  Remaining Bottlenecks / Recommendations

  - Two sessions sit idle in transaction; ensure the client closes transactions promptly to avoid holding locks unnecessarily.
  - Continue monitoring pg_stat_wal/pg_stat_database deltas to ensure flush latency stays sub-millisecond; the new config and batching are working so far.
  - Since the app is now the primary CPU consumer, profile request handling in DMS (per-request batching, JSON serialization, etc.) to chase further latency wins.
  - Keep an eye on WAL volume (≈255 MB in 30 s) so you can size archive/log storage and replication accordingly.

  Everything on the database side now looks efficient; the alias index eliminated the prior cascade scans, and WAL flushes are fast. Next logical step is application profiling to trim remaining
  response time or evaluate if additional batching can reduce overall commit rate.

  Check in on load tester

  - The box still has headroom: top at 16:57:37 shows aggregate CPU 38 % user / 5 % system / 1.8 % wait, leaving 54 % idle. That’s with the Python load client (PID 129622) at ~83 % CPU (≈0.8 core),
    the DMS service around 260–300 % (≈3 cores), and the busiest Postgres backends between 30–40 % each.
  - Disk isn’t stressed (iostat reports ~0.11 ms write waits even while the test runs), so the client’s activity isn’t pushing I/O queues up.
  - Network traffic is local (loopback), so there’s no external bottleneck; the primary effect of the Python process is simply generating the load you asked for.

  Bottom line: the load generator is consuming a fraction of the available CPU but the system remains more than half idle, so it isn’t interfering with the DMS app. If you ever must co-locate them
  in production, you could pin cores or run the tester elsewhere, but it’s not necessary for these tests.

   ## Update - 2025-10-26 17:28 (all above, but brought wal_level to logical - a prereq for replication)
  FYI, 5ms median, 6ms avg


 • WAL-Level Shift

  - Since resetting at 17:33, pg_stat_wal shows ~600 MB WAL produced in 30 s (17:46:17 → 17:46:52), with ~97 k extra wal_records and wal_fpi jumping by ~82 k. Logical wal inserts extra row-image
    metadata, so expect ~10–12 % more WAL bytes per commit, as seen here (≈30 MB → 46 MB delta compared to the earlier replica run).
  - wal_sync_time increased accordingly: +15.9 s across +30 ~82k syncs implies ~0.19 ms per flush; still low, but accumulating more total WAL time (≈300 ms extra per 30 s window).
  - No replication slots are active, so the extra WAL is just retained in pg_wal. Ensure archiving/retention accommodates the higher volume.

  Database Bottlenecks

  - WAL waits remain minimal: 1 backend at a time in WALSync/WALWrite, typically during COMMIT, with latency in the sub-millisecond range. Disk keeps up (iostat w_await ≈0.10–0.12 ms, ~3.5 k fsync/
    s).
  - Autovacuum still handles dead tuples (document partitions ≤15 k dead rows, 6–8 autovacs).
  - pg_stat_database confirms lively throughput: ~100 k commits per 30 s (~3.3 k/s), inserts/deletes around 120 k/s combined. No database-side blocking beyond short idle in transaction sessions (1
    left open).

  System-Level

  - The DMS application is now the dominant CPU load. pidstat shows EdFi.DataManage… averaging 280 % CPU with no wait time. top highlights the app and a python driver consuming more CPU than any PG
    backend. Postgres workers sit at 25–35 % each—no longer the limiting factor.
  - Load averages remain ~11, with plenty of idle CPU (~53 %) and low I/O wait (~2 %).

  Next Steps

  1. Monitor WAL growth: logical level adds overhead; track archive size and consider wal_keep_size adjustments.
  2. Profile the DMS app and the python orchestrator—these are now the primary sources of response-time pressure.
  3. Keep client sessions from lingering idle in transaction (close or commit quickly) to avoid future contention.
  4. If WAL volume becomes a concern, explore logical decoding output plugins tuned for your use—or revert to replica once tests that require logical level finish.

  Overall, moving to wal_level=logical increased WAL output and sync time, but the storage and commit path remain healthy. The main bottleneck shifted to the application tier; focus further
  optimization there.

   ## Update - 2025-10-26 17:28 (all above, but brought wal_level to logical + replica full)

• What changed with wal_level = logical + REPLICA IDENTITY FULL

  - WAL volume per commit roughly doubled. Since the reset at 18:15 CDT, pg_stat_wal shows 7.9 GB of WAL for 2.48 M commits—~3.2 KB/commit versus ~1.6 KB/commit before the change. wal_fpi climbed
    to 2.0 M tuples (none previously), reflecting full-page images plus entire row images now logged for every update/delete.
  - Flush cost stayed similar per sync (~0.34 ms), but the higher commit rate meant 1.06 M WALSync events in 30 s, keeping the NVMe busy (~3.3 k fsyncs/s at 0.11 ms per iostat), although still
    below saturation (≈40 % util).
  - Table churn increased sharply for the alias partitions: alias_00 and peers now show 26–30 k dead tuples each with only 3–4 autovacuum passes (pg_stat_all_tables), compared to a few thousand
    earlier. Autovacuum is running continuously (autovacuum: VACUUM dms.document_01 in pg_stat_activity and a long-lived pg_stat_progress_vacuum entry) just to keep up.

  Current Bottlenecks

  - Write workload is now dominated by logging whole-row images. High wal_bytes and wal_fpi are the main source of extra I/O; deletes/updates still execute quickly (alias delete plan finishes in
    0.38 ms thanks to the new index), but every change now emits large WAL records.
  - Autovacuum pressure: alias partitions accumulate tens of thousands of dead rows quickly, so vacuums will be more frequent/longer. Expect higher background I/O and CPU from vacuum workers,
    especially if workloads spike further.
  - Application tier remains the largest CPU consumer: EdFi.DataManage… still runs at ~275 % CPU via pidstat, while individual Postgres backends sit at 35–45 %. So overall response time is now
    bounded by the DMS workload pattern plus the heavier WAL logging. No OS-level contention yet (load avg 11 on 24 cores, vmstat idle ~57 % and wait ~2 %).

  Recommendations

  1. Reconsider whether REPLICA IDENTITY FULL is necessary. If Debezium can rely on a primary key (documentpartitionkey, documentuuid), switch to REPLICA IDENTITY USING INDEX to avoid full-row WAL
     logging. The current setting doubles WAL size and raises autovacuum cost.
  2. If you must keep FULL, scale infrastructure accordingly: enlarge WAL/archive storage, raise max_wal_size, and ensure replicas/consumers can ingest the additional volume. Enable logical
     replication slots only when ready to stream, so WAL isn’t retained unnecessarily.
  3. Tune autovacuum for alias/document tables (lower autovacuum_vacuum_scale_factor, dedicate more workers) so they can keep ahead of the dead tuples produced by logical decoding-friendly logging.
  4. Keep monitoring pg_stat_wal, pg_stat_database, and pg_stat_progress_vacuum per test run; the WAL deltas you captured over 30 s (~160 MB, ~375 k records) are now the baseline to beat.
  5. Continue profiling the DMS application path, since it still accounts for the majority of CPU and drives the database commit rate; batching and transaction management there will have the
     biggest impact on overall response times.

   ## Update - 2025-10-26 18:43 (all above, but brought wal_level to logical + replica identity)



TRUNCATED
    despite the higher WAL volume from logical encoding.
  - Database throughput remains high: commits climbed from 2.10 M to 2.55 M in 15 minutes (~5 k/s), deletes ~1.07 M. Compared to the physical run (~2.8 k commits/s), the workload actually
    increased, yet flush latency stayed steady.

  Schema & Triggers
    document delete path remains index-driven.

  Remaining Waits

  - Dead tuples have grown (alias_03 ~30 k, document_00 ~12 k). Autovacuum counts (3–6) imply it’s working, but consider lowering autovacuum_vacuum_scale_factor on these hot partitions to keep
    dead rows from piling up under sustained logical logging.

  System-Level View

  - Disk: iostat under the new load sees ~2.5 k fsyncs/s with 0.14 ms waits, ~11–32 MB/s writes—still well within NVMe limits.
  - CPU: the DMS app is now the dominant load (pidstat on EdFi.DataManage… ~280 % CPU, top shows the app plus Python generator consuming more than all Postgres workers combined). The database side
    hovers 35–90 % per backend, but overall CPU headroom remains (≈55 % idle).
  - Memory/Swap: system is using ~4.6 GB of swap (per top). If not intended, check JVM/.NET heap settings for DMS; swapping could harm response time even though DB is healthy.

  Conclusions

  - Switching to wal_level=logical and default replica identity doesn’t introduce new database bottlenecks; WAL flush latency remains sub-millisecond, and index-driven cascades keep write
    operations snappy.
  - The main constraint now lies in the DMS application tier (high CPU usage, swap). Further response time improvements will come from profiling/batching in the app and ensuring it doesn’t sit
    idle in transaction.
  - For ongoing tuning: monitor pg_stat_wal deltas per run, tighten autovacuum thresholds on document/alias partitions, and watch for long-lived transactions that may interfere with logical
    decoding.

  Overall the database is ready to sustain logical WAL workloads; focus next on optimizing the application pipeline and resource settings.

   ## Update - 2025-10-27 15:11 (all above, but added sequential DocumentUuid)

DB Observations

  - With track_wal_io_timing enabled, the latest 30 s sample (18:46:02–18:46:32 CDT) shows 49 040 WAL flushes with wal_sync_time increase 16 378 ms → avg 0.33 ms per flush, while
    wal_write_time climbed only 719 ms (0.015 ms/write). Group commit is effective: ~99 745 commits were recorded in the same interval, so each flush covers ~2 commits.
  - WAL volume for that window was ~55 MB (≈1.9 MB/s) with wal_buffers_full = 0, indicating neither WAL size nor buffers are throttling throughput.
  - Workload mix per 30 s: +41 k deletes, +41 k inserts, +8.9 k updates—so writes remain heavy but now largely batch into each commit. No sustained WALWrite/WALSync waits appeared;
    only sporadic single sessions were caught waiting on WAL.
  - pg_stat_bgwriter since the latest reset (18:31 CDT) shows 3 scheduled checkpoints taking 538 s of write time to push ~1.5 M buffers, plus 33 k backend writes. That level is
    acceptable but watch for more CheckpointWriteDelay events if throughput grows.
  - Table stats look healthy. dms.document_* partitions report 1–7 k dead tuples each with autovacuum count 16–20, and GIN/BTREE indexes show almost exclusively cache hits—
    sequential UUID adoption appears to be keeping page-split pressure low.
  - pg_stat_database.temp_bytes accumulated ~1.9 GB since reset, so some queries (likely in the DMS app) still spill to disk; enable pg_stat_statements or inspect application SQL
    to identify which sorts/hashes are involved.

  System Observations

  - Host CPU is the current ceiling: top at 18:47:51 shows load average 11.0 with EdFi.DataManagementService using ~217 % CPU and several Postgres backends at 25–42 % each. Overall
    CPU utilization stays ~36 % user / 6 % system, only 2 % iowait.
  - Memory pressure is modest (≈1.1 GB free, 52 GB page cache) but swap already holds ~2.9 GB; if that grows it could hurt response times.
  - Disk activity is negligible during the sampled slice (iostat shows ~0 ops/s), implying the hot working set fits in cache and latency is dominated by CPU and application-level
    work.

  Recommendations

  1. Keep tracking group-commit efficiency: periodically capture 30 s deltas of wal_sync_time, wal_sync, and xact_commit to ensure ~0.3 ms/flush and <0.6 flushes/commit hold as
     load increases.
  2. Instrument the DMS application: its 200 %+ CPU share suggests client-side processing (serialization, batching, JSON work) may now govern response time. Add timing around
     batched commit blocks and any JSON transformations to confirm.
  3. Install and enable pg_stat_statements (if acceptable) so you can tie the 1.9 GB of temp spill and any long-running statements to specific queries; then tune work_mem per query
     or add supporting indexes as needed.
  4. Watch checkpoint cadence: if buffers_backend keeps rising, consider increasing max_wal_size or shortening checkpoint_timeout to smooth spikes, and continue monitoring for
     CheckpointWriteDelay waits.
  5. To catch new bottlenecks early, add a lightweight Grafana/Prometheus or pganalyze dashboard tracking CPU per process, WAL flush latency, checkpoints, and temp bytes—especially
     valuable before pushing this workload to a stricter SLA.

  Next step I’d take is sampling pg_stat_statements (or application logging) once the extension is in place so we can pinpoint any query still triggering temp files and validate
  the DMS-side CPU work.

## Update - 2025-10-27 22:15 (all above, on PG 18)

• Database View
    stalls are no longer the source of delay.
  - pg_stat_wal grew by ~473 MB in 30 s (wal_bytes 8 861 610 283→9 334 854 530), or ~15 MB/s for ~92 k commits, with wal_buffers_full = 0; WAL volume is high but buffered
    efficiently.
  - pg_stat_io (30 s delta) shows 19 walwriter flushes totaling 7.6 ms (0.40 ms/flush) and 43 k client-initiated flushes totaling 14.5 s (0.33 ms/flush). The dominant cost remains
    “one fsync per statement” with synchronous_commit = on`, not slow storage.
  - pg_stat_statements highlights the workload mix: DELETE (mean_exec_time ≈ 2.09 ms, 387 k calls), INSERT CTE (0.40 ms, 387 k), SELECT-by-UUID (0.07 ms), UPDATE (0.14 ms), plus
    958 k DISCARD ALL resets—query execution itself is quick.
  - pg_stat_checkpointer since 22:17 shows 16 timed + 16 requested checkpoints with 2.70 s write and 2.24 s sync time against 8.6 M buffers written, confirming smooth checkpoint
    behavior.

  System View

  - top at 22:40 reports load average 10.8/9.7/6.5 with plenty of idle CPU (58 %), but the DMS service (EdFi.DataManagementService, PID 193043) is consuming ~250 % CPU and the load
    driver (python, PID 222093) ~92 %. Multiple Postgres backends are each at 33–75 % CPU. Application CPU saturation is therefore the most visible response-time limiter.
  - Memory is mostly page cache (52 GiB). Only 1.5 GiB free, and 4.9 GiB of swap is in use—worth watching, though 44 GiB remain available via cache drop.
  - vmstat 1 5 shows the system steady at ~37 % user, ~5 % system, ~56 % idle, and minimal IO wait (~2 %) despite the high load average; the database is CPU-driven, not IO-bound.

  Bottleneck Assessment

  - PostgreSQL’s WAL subsystem is keeping up: fsync latency is sub-millisecond, no buffer saturation occurs, and checkpoints are timely. High WAL volume stems from the ingest
    pattern (hundreds of thousands of tiny transactions).
  - PostgreSQL query times are low; there’s no evidence of SQL-level hot spots or lock contention. The lone idle in transaction session should still be closed to avoid surprises.
  - The DMS application itself is the heaviest CPU consumer. With DISCARD ALL executed on nearly every request, connection pooling is likely flushing session state each time—this
    may add overhead on both the app and database tiers.
  - Autovacuum is active but not blocking; keep an eye on it if latency spikes coincide with vacuum cycles.

  Next Steps

  1. If ingest durability allows, batch multiple statements per transaction or set synchronous_commit = OFF (or LOCAL) for the loader sessions to cut the 0.3 ms fsync penalty per
     request.
  2. Investigate why EdFi.DataManagementService is pegging >2 cores; profile the DMS code paths, and verify the client reuses prepared statements instead of issuing DISCARD ALL
     each checkout.
  3. Clear the lingering BEGIN session (pid 222226) and consider tightening connection pool settings to avoid idle-in-transaction states.
  4. Track swap usage during the remainder of the test; if it keeps rising, raise vm.swappiness or adjust the service to release memory sooner.

Follow-up on the DISCARD ALL:

• DISCARD ALL is PostgreSQL’s “reset this session to factory defaults” command. The pg_stat_statements sample we pulled (queryid 3544278337386968096, 957 729 calls, mean runtime
  0.019 ms) shows it being issued almost once per application round-trip. That pattern matches how the Npgsql provider (and other drivers) sanitize a connection whenever it’s
  closed or returned to the pool: they send DISCARD ALL to drop prepared statements, temp tables, GUC changes, etc.

  Because you’re seeing nearly one DISCARD ALL per DML statement, the DMS service is treating connections as throwaways—open, run a single INSERT/UPDATE/DELETE, reset with DISCARD
  ALL, repeat. The individual command is cheap, but that usage still incurs extra network chatter, session setup (SET search_path ... reappears in pg_stat_activity), and prevents
  server-side plans from being reused effectively.

  If that wasn’t intentional, look at the .NET connection management:

  - Confirm the service is using Npgsql’s built-in pooling (Pooling=true in the connection string) and isn’t explicitly calling NpgsqlConnection.ClearPool or opening with No Reset
    On Close=false per request.
  - Keep the pool size high enough that connections stay warm between requests; short timeouts or aggressive dispose patterns will keep triggering the reset.
  - If you really need the reset semantics, consider letting PgBouncer handle pooling in transaction mode so Npgsql doesn’t have to issue DISCARD ALL on every close.

  In short, the resets themselves aren’t the bottleneck, but they’re a strong signal that connection reuse isn’t happening and you’re paying extra overhead in the DMS layer.

## Update - 2025-10-27 22:15 (all above, SELECT FOR UPDATE locks back on)

• Postgres 18 Snapshot

  - pg_stat_wal climbed from 10.8 GB to 12.0 GB in 30 s (≈1.18 GB delta ≈39 MB/s) with 15.1 M WAL records; WAL buffers aren’t filling (wal_buffers_full = 0).
  - pg_stat_io shows the walwriter handled 1 535 writes in 75 ms total write time and 572 ms total fsync time (≈0.37 ms each), so flush latency is low; pg_stat_checkpointer logged
    3 completed checkpoints since reset, writing 1.22 M buffers with 809 s cumulative write time.
  - pg_stat_statements highlights DML as the dominant time sink: the DELETE FROM dms.Document… statement has 434 k calls with 887 s total time (≈2.0 ms mean), while the INSERT …
    CTE contributes 153 s. The “SELECT … FOR NO KEY UPDATE” join executes 669 k times (0.03 ms mean) and now reports 11.5 MB of WAL, confirming row-locking SELECTs add some WAL
    traffic.
  - Expensive one‑off probes remain: SELECT count(*) FROM dms."document" averages 1.24 s (2 calls), SELECT count(*) FROM dms."alias" ~168 ms (3 calls) — they sweep entire
    partitions.
  - Document partitions still carry modest churn (n_dead_tup 5–8 k each, autovacuum_count 6–7); buffer stats show ~200 k heap blocks read and 3.6 M hits per hot partition since the
    last reset.

  Locking Check

  - Repeated sampling (pg_stat_activity, pg_blocking_pids) found no sessions waiting on Lock; pg_locks has no ungranted entries. SELECT … FOR NO KEY UPDATE calls are finishing
    quickly.
  - Two connections are regularly left idle in transaction after those SELECT FOR UPDATE queries, so row locks persist until the client finishes; this isn’t blocking yet but raises
    risk under heavier concurrency.
  - No tuple-lock rows are visible at the sample times; if you need continuous visibility, consider monitoring pg_locks filtered on locktype = 'tuple' at higher frequency.

  System Bottlenecks

  - OS load is CPU-bound: top shows the DMS ASP.NET process at ~290 % CPU, the Python load driver at ~82 %, and several postgres backends/autovacuum between 36 – 73 %. Load average
    is 11.4 even though disk waits sit near 0.1 ms.
  - Autovacuum workers can spike to 5.5 GB RSS and >70 % CPU (with maintenance_work_mem = 2 GB), competing with foreground work during large sweeps.
  - The host is carrying 3.3 GB of swap in use, though no active paging is occurring; disk on /dev/nvme0n1p3 is sustaining ~3.5 k writes/s at ~0.11 ms wait, so I/O isn’t the gating
    factor.

  Recommendations

  1. Profile the DMS application while the test runs (e.g., dotnet-trace, dotnet-counters) — it’s the top CPU consumer and will drive response-time variance more than the database
     right now.
  2. Ensure client code commits/rolls back immediately after SELECT … FOR UPDATE/NO KEY UPDATE; add instrumentation to capture the offending callers and consider tagging
     connections via application_name for easier tracking.
  3. Keep watching WAL growth with the new PG 18 counters: schedule periodic pg_stat_wal snapshots and correlate with throughput; if commit latency climbs, reevaluate batching or
     synchronous_commit for this workload.
  4. Tame autovacuum impact by lowering autovacuum_vacuum_scale_factor (to trigger smaller, faster runs) or reducing maintenance_work_mem from 2 GB so vacuum shares CPU/memory more
     gracefully during load tests.
  5. Eliminate or cache the full-table count(*) probes and investigate why the pool issues 1.07 M DISCARD ALL calls (seen in pg_stat_statements); both add avoidable work during
     stress runs.

Follow up on transient open transactions

• Idle-In-Transaction Sessions

  - Captured at 16:11:22–16:11:25 CDT, two backends (e.g., pid 363837 and pid 363840 from 127.0.0.1 with empty application_name) entered state = idle in transaction immediately
    after SELECT … FOR NO KEY UPDATE and the WITH Documents … INSERT … RETURNING CTE. Their xact_age and state_age were ≈7–10 ms, and wait_event_type = ClientRead, indicating the
    server is waiting for the client to finish the transaction.
  - While in that brief state they hold table-level locks across the entire partition set: RowShareLock on dms.document, every dms.document_00…document_15 child table, their
    PK/unique indexes, and the dms.alias table/indexes, plus RowExclusiveLock on dms.alias and the usual transactionid / virtualxid locks. (Example mapping from pg_locks:
    OID 16688→dms.document, 16706→dms.document_00, … , 17044→dms.alias, 17027→document_00_documentpartitionkey_documentuuid_idx, 18421→ix_document_resourcename_createdat.) If these
    sessions linger they can block other writers touching any partition.
  - Repeated 1 Hz sampling for 60 s after that burst saw no further idle in transaction rows, so the pattern appears as very short-lived gaps rather than sustained transactions;
    nevertheless they recur frequently enough to notice in pg_stat_activity.

  Next Diagnostics

  - Run this view during load to catch offenders with full metadata:

    WITH idle AS (
      SELECT pid, now()-xact_start AS xact_age, now()-state_change AS state_age,
             application_name, client_addr, left(query,200) AS query
      FROM pg_stat_activity
      WHERE datname = 'edfi_datamanagementservice' AND state = 'idle in transaction'
    )
    SELECT idle.*, l.locktype, l.mode, c.relname
    FROM idle
    JOIN pg_locks l USING (pid)
    LEFT JOIN pg_class c ON l.relation = c.oid
    ORDER BY pid, locktype, relname;
  - Enable connection tagging in the app (SET application_name) so you can tie these sessions back to specific code paths, and consider setting idle_in_transaction_session_timeout
    (e.g., 2–5 s) as a safeguard.
  - If you need longer history, log these events via log_min_duration_statement plus log_lock_waits = on to flag when a SELECT … FOR UPDATE/NO KEY UPDATE finishes but the
    transaction lingers.

  In short, those “idle in transaction” copies are the loader connections waiting on the client after grabbing row locks; they only last a few milliseconds now but hold locks
  across every document partition. Tighten the client commit/rollback handling and add identification to keep an eye on them in future runs.

  ## Update - 2025-10-29-15-57 (all above, reference loaded)

DB Findings

  - pg_stat_wal (reset 15:45:15 CDT) shows 34 077 584 WAL records, 6 460 399 FPIs, and 24.86 GB written—≈16.96 MB/s over the past ~30 minutes—and zero wal_buffers_full, so the WAL
    path is keeping up. pg_stat_io reports client backends flushing 5 159 422 WAL fsyncs at 0.335 ms each and the walwriter 27 823 fsyncs at 1.76 ms, confirming the datastore is not
    WAL‑bound right now.
  - Wait sampling (pg_stat_activity) is dominated by ClientRead; only one backend at a time is seen on IO|WalSync / LWLock|WALWrite, and DML statements complete quickly
    (pg_stat_statements: DELETE dms.Document… mean 1.73 ms for 1.43 M calls, INSERT 0.33 ms for 1.53 M calls, UPDATE 0.11 ms for 0.67 M calls). Heavy WAL producers are the document
    INSERT CTE (4.31 GB WAL) and document UPDATE (1.06 GB) but their runtimes stay sub‑millisecond.
  - The new dms.reference_* partitions already hold ~1.25 M rows each (~170 MB per partition) with no accumulated dead tuples yet. Autovacuum is continuously active on hot document
    partitions (pg_stat_progress_vacuum currently shows workers on dms.document_15 and _08), which is keeping dead tuples around 5 K per partition.
  - Memory settings are aggressive: maintenance_work_mem=2097152 (2 GB) and work_mem=65536 (64 MB). Autovacuum workers (e.g., PID 631460) are consuming up to 7.7 GB RSS, and many
    client backends sit at ~2.5 GB each, a direct consequence of these settings plus 22 concurrent sessions.

  System Findings

  - free -h shows only 1.5 GB free and 7.2 GB of the 8 GB swap in use; vmstat 1 5 (latest sample above) records ongoing swap in/out (first row si 55, so 129). The swap pressure, not
    the WAL subsystem, is the biggest current risk to response time.
  - pidstat -r/-u highlights the memory footprint (multiple postgres backends 2–7 GB RSS) and CPU profile: total CPU sits around 33 % user / 6 % system / 60 % idle, while the DMS
    process EdFi.DataManage alone burns ~474 % CPU (≈5 cores) and the Python load generator another ~90 %. Most postgres backends are utilizing ~30 % CPU with plenty of headroom,
    suggesting the application layer may now dominate perceived latency.
  - Disk remains responsive—iostat was calm during the sample—but pg_stat_io shows 105 GB of WAL and 109 GB of heap writes since the reset (~61 MB/s on average). NVMe is coping, yet
    sustained churn amplifies autovac and checkpoint work.

  Assessment

  - Database write performance is healthy: WAL flush times are low and wait events show no write blocking.
  - The main bottleneck is memory pressure from oversized maintenance_work_mem and work_mem interacting with many concurrent autovacs and client sessions; the 7 GB swap usage and
    measurable swap activity will eventually erode response time and could explain any spikes observed during the run.
  - End-to-end response time is likely constrained on the DMS side: most backends wait on the client, while the application process consumes several CPU cores doing non-database work
    (e.g., JSON handling).

  Recommendations

  1. Trim memory settings immediately:
      - Reduce maintenance_work_mem to something safer (e.g., 256–512 MB). That alone will drop autovacuum RSS from multi‑gigabyte levels and curb swap churn.
      - Lower work_mem globally (e.g., 16–32 MB) and override per session only when needed. With 22 concurrent sessions, each 64 MB allocation adds up quickly.
      - After adjusting, restart PostgreSQL and confirm with free -h/vmstat that swap usage falls below ~1 GB.
  2. Keep leveraging PG 18 monitoring:
      - Continue watching pg_stat_io with object='wal' to track fsync latency; today’s averages are excellent benchmarks.
      - Track the FPI ratio (wal_fpi/wal_records, currently ~19 %) and run standard VACUUMs on the busiest partitions if it rises, to avoid repeated first-page image logging.
  3. Manage autovac concurrency carefully: with a lower maintenance_work_mem, autovacuum_worker_slots=16 is manageable, but if memory remains tight consider capping it closer to 6‑8 to
     prevent many simultaneous 2 GB workers.
  4. Investigate the DMS application:
      - Profile the EdFi.DataManage process to see whether JSON serialization, downstream services, or network calls are adding latency while the database waits idle.
      - Confirm the ingest still batches operations sensibly; reducing the 1.8 K commits/sec rate would shrink the 17 MB/s WAL stream and reduce autovac load.
  5. Use pg_stat_statements snapshots per test to compare query runtimes and WAL production; exclude tooling queries like the SELECT d.* ORDER BY d.id DESC (287k temp blocks) during
     load tests to keep temp I/O noise down.

  Once the memory changes are in place, rerun the load test with the same metrics (pg_stat_wal/io/statements plus OS snapshots) to verify that swap pressure disappears and that the DB
  remains wait-free; if response issues persist, focus tuning on the DMS application layer.

  ## Update - 2025-10-29-15-57 (all above, reference inserts)


  • Observations

  - WAL volume is now extreme: pg_stat_wal grew by 1.08 GB in 30 s (≈36 MB/s), and pg_stat_io shows client backends have issued 6.9 M WAL fsyncs since the reset with ~0.34 ms
    apiece, so latency is dominated by sheer commit count rather than slow storage.
  - The new reference workload is the top SQL cost centre: pg_stat_statements reports SELECT d.* … INNER JOIN dms.Reference … averaging 101 ms over 2 415 calls, while
    each reference partition holds ~1.25 M live rows plus ~37 K dead rows (pg_stat_all_tables), implying the join scans every partition because the list partition key
    (parentdocumentpartitionkey) does not match the filter (referentialpartitionkey, aliasid).
  - Reference insertion via SELECT dms.InsertReferences(...) now accounts for 1 131 s of total execution time (2.33 ms per call) and drives the spike in WAL/HOT churn together with
    425 K document deletes.
  - Autovacuum is active but falling behind the reference partitions: each has only three autovac runs since the last reset and tens of thousands of dead tuples;
    pg_stat_progress_vacuum shows long vacuums running on document partitions during the test window.
  - System pressure is significant: EdFi.DataManage is the top consumer at 166 % CPU, swap usage sits at 7.7 GiB/8 GiB with non-zero swap-in/out in vmstat, and overall load
    averages 12–10–8 despite idle disk, so the DMS application and swapping are likely adding response-time jitter beyond PostgreSQL.

  Recommendations

  - Revisit the dms.reference partitioning strategy: either partition by (referentialpartitionkey) (or hash) to enable partition pruning for the alias lookups, or create a covering
    global index (e.g. CREATE INDEX ON dms.reference(referentialpartitionkey, aliasid, parentdocumentpartitionkey, parentdocumentid)) to avoid 16 partition probes per call.
    Validate with EXPLAIN once applied.
  - Tune the reference maintenance path: lower autovacuum_vacuum_scale_factor for the reference partitions (and possibly alias partitions) and consider batching deletes so autovac
    catches up before dead tuples accumulate; monitor with pg_stat_progress_vacuum.
  - Manage WAL pressure by reducing commit frequency (batch the reference insert/delete transactions or use synchronous_commit = LOCAL/OFF for the ingest workers) and keep an eye
    on pg_stat_io’s WAL fsync counters to ensure average flush time stays sub-ms.
  - Address system-level swapping: either provision more RAM, cut the DMS application’s working set/concurrency, or add swapless caches—swap thrash is already measurable and will
    hurt both PostgreSQL and application response time.
  - Keep using the new monitoring: reset pg_stat_wal, pg_stat_io, and pg_stat_statements between runs (SELECT pg_stat_reset_shared('wal'); SELECT pg_stat_statements_reset();) so
    each test yields clean deltas, and baseline the 101 ms join again after schema/index changes.

  Natural next step: apply the schema/index or autovacuum adjustments in staging, rerun the load, and compare pg_stat_statements mean times plus WAL deltas to confirm the
  bottleneck is relieved.


  ## Update - 2025-10-30-13-24 (all above, reference fix #3)

Enabled pg_stat_statements after pausing ~10 minutes, then sampled the system to isolate current hotspots.

  Database Observations

  - pg_stat_statements shows SELECT dms.InsertReferences($… ) dominating runtime (379 s total, 2.5 ms mean) and generating ~1.97 KB WAL per call; the accompanying DELETE/INSERT on
    dms.Document add another 238 s. Together they account for ~45 % of the recorded execution time and 0.65 GB of WAL (wal_bytes column).
  - pg_stat_io highlights WAL syncing pressure: client backends have performed 277 k WAL writes with 94.9 s cumulative fsync time (≈0.34 ms per flush) since 13:05. pg_stat_activity captured
    commits waiting on WalSync, confirming synchronous flush latency as the main bottleneck.
  - pg_stat_wal reports 6.46 M WAL records / 990 MB generated in the last ~11 minutes. Checkpointer statistics (pg_stat_checkpointer) show frequent checkpoints (178 timed, 18 requested)
    with 7.5 s total write time over the current interval.
  - Autovacuum is keeping up: each dms.reference_* partition shows 4–5 autovacuums since the last reset with dead tuples ≲5 % of live rows (pg_stat_all_tables). Hit ratio remains high
    (pg_stat_database: 1.57 B hits vs. 1.33 M reads).

  App & Load Test

  - The EdFi.DataManagementService process is using ~225 % CPU (≈2.3 cores) while individual PostgreSQL backends consume 40–70 % each (top). No runaway memory usage detected (postgres
    backends at ~3 GB RSS apiece).
  - Load generator /home/brad/.../edfi-performance-test sits at ~79 % CPU, 60 MB RSS, and only 15 KB/s writes (pidstat), so it is unlikely to throttle itself.
  - Latest results (Suite-3-Performance-Testing/DmsTestResults/2025-10-30-13-01-with-reference-fix-3/volume_stats.csv) show ~1.21 k req/s with median latency 7 ms, 99.9 % at 35 ms, max
    334 ms—no broad response-time degradation. However, volume_failures.csv records 244 POST failures (HTTP 400) for /data/ed-fi/studentSchoolAssociations; these are functional errors, not
    transport issues, but they do skew success metrics.

  Recommendations

  1. Prioritize reducing churn inside dms.InsertReferences (e.g., switch from delete+bulk insert to differential updates or INSERT … ON CONFLICT) to cut WAL volume and commit sync pressure.
  2. Evaluate WAL configuration once the functional change is in flight: larger wal_buffers, slower checkpoint cadence, or (if replication allows) synchronous_commit = off/local can further
     trim WalSync waits.
  3. Investigate the repeated 400 responses in the load test to ensure they are expected; otherwise they may mask performance regressions.
  4. Keep tracking pg_stat_io and pg_stat_statements after adjustments to confirm WAL fsync time drops and high-frequency queries stay within latency targets.

  Let me know if you’d like deeper analysis of the InsertReferences procedure or assistance applying any of these tunings.

  ## Update - 2025-10-30-23-41 (all above, insert references using NEW-MERGE)

  Findings

  - InsertReferences dominates database time (1.89×10⁶ ms ≈ 79% of all tracked SQL); 758 k calls average 2.5 ms (max 71 ms) and generate 4.9 GB of WAL plus 146 M shared-buffer hits, so the
    workload is CPU/WAL bound rather than waiting on I/O.
  - Every call recreates session-local state because the pool issues DISCARD TEMP 956 k times (163 s cumulative) immediately after the function runs, defeating ON COMMIT PRESERVE ROWS and
    forcing CREATE TEMP TABLE…TRUNCATE catalogue activity on each invocation.
  - High-churn tables show notable dead tuples: each dms.reference_* partition holds ~95 MB with 6–28 k dead rows and only 3–5 autovac runs since the last reset; autovacuum is active but
    struggling to keep bloat low under the current delete/insert pattern.
  - System headroom looks healthy: CPU averages 36% user with 2–3% iowait, NVMe writes sit around 65 MB/s with ~0.1 ms latency, postgres backends top out near 47% CPU, the DMS ASP.NET
    process at ~2.5 cores (253%), and the Python load driver uses ~0.8 core—no evidence the generator itself is the bottleneck.

  Recommendations

  - Refactor InsertReferences staging so pooled sessions stop dropping the temp table—either switch to an unlogged per-backend staging table keyed by pg_backend_pid or adjust Npgsql pooling
    (No Reset On Close=true and explicit cleanup) so DISCARD TEMP is avoided.
  - Enable track_functions = pl (with pg_stat_statements.track = all) during a future run to capture in-function SQL timings and confirm whether the DELETE … NOT EXISTS stage is consuming
    the unexpected buffer volume.
  - Tighten autovacuum settings on hot partitions (e.g. ALTER TABLE dms.reference SET (autovacuum_vacuum_scale_factor=0.01, autovacuum_analyze_scale_factor=0.005,
    autovacuum_vacuum_threshold=500) and consider partition-level scheduling) to keep dead tuples from inflating buffer churn.
  - Review the application write pattern that performs DELETE FROM dms.Document + reinsert per upsert; if feasible, switch to UPDATE with partial JSONB patches so cascading deletes stop
    amplifying WAL and vacuum pressure.

  Next Steps

  - Capture EXPLAIN (ANALYZE, BUFFERS) for representative InsertReferences executions in a staging environment after staging-table adjustments to validate plan stability.
  - Re-run the volume test once pooling/autovacuum changes land and compare pg_stat_statements shares plus WAL throughput to confirm the bottleneck has shifted.


  From DMS side - Before any changes:
• Captured EXPLAIN (ANALYZE, BUFFERS) for three representative dms.InsertReferences calls before any changes

  - Valid request with a duplicate referential ID (shows dedup path):

    BEGIN;
    EXPLAIN (ANALYZE, BUFFERS) SELECT dms.InsertReferences(
        11::bigint,
        0::smallint,
        ARRAY['98e731c5-ee3d-f557-78f8-6018f4ab09e0'::uuid,
              '98e731c5-ee3d-f557-78f8-6018f4ab09e0'::uuid],
        ARRAY[0::smallint, 0::smallint]
    );
    ROLLBACK;
    Output (actual 27.93 ms, shared hit=3054/read=78/dirtied=38; local hit=3/dirtied=1/written=1; shared read I/O 8.91
    ms).
    ms).

  - Valid request with three different referential IDs:

    BEGIN;
    EXPLAIN (ANALYZE, BUFFERS) SELECT dms.InsertReferences(
        12::bigint,
        0::smallint,
        ARRAY['98e731c5-ee3d-f557-78f8-6018f4ab09e0'::uuid,
              'ef1bb27b-7890-0bd4-4c64-63e4a58f13c0'::uuid,
              'c7e50a05-5281-84fa-51c7-bec5544726d0'::uuid],
        ARRAY[0::smallint, 0::smallint, 0::smallint]
    );
    ROLLBACK;

    Output (actual 45.93 ms, shared hit=3162/read=10/dirtied=8; local hit=5/dirtied=1/written=1; shared read I/O 34.58
    ms).

  - Request containing an invalid referential ID (produces FALSE return and no upsert work):

    BEGIN;
    EXPLAIN (ANALYZE, BUFFERS) SELECT dms.InsertReferences(
        11::bigint,
        0::smallint,
        ARRAY['00000000-0000-0000-0000-000000000000'::uuid],
        ARRAY[0::smallint]
    );
    ROLLBACK;

    Output (actual 12.66 ms, shared hit=2719/read=6/dirtied=12; local hit=3/dirtied=1/written=1; shared read I/O 0.90 ms).

  Every run returns only the top-level function node in the plan tree (expected for EXPLAIN around a function call), but
  the timings and buffer usage capture the end-to-end cost of each representative execution.

Further auto-explain stuff

• Observations

  - Duplicate-ID call: staging performs a Window/Sort dedupe before inserting into the temp table (0.38 ms, /var/log/postgresql/postgresql-2025-10-31_095909.log:41); the overall function
    still touches ~3 k shared buffers and pulls 313 pages from disk (36 ms total, ...:488).
  - The same call’s WITH upsert is dominated by the anti-join delete: it scans 10 reference rows, deleting all of them and generating 13 WAL records (4.5 KB) plus 30 FPIs
    (lines ...:361, ...:383, ...:399). Only one row is inserted, yet the delete churn outweighs the insert (...:367).
  - Each invocation issues SELECT … FOR KEY SHARE against dms.document and dms.alias, which shows up as extra latency and full-page images even though these are read locks
    (...:176, ...:244, ...:998).
  - Invalid-ID call: staging keeps the row (alias NULL) but the insert step filters it out, then the delete still removes all 10 existing references (WAL records=10) before the function
    returns false (...:527, ...:710, ...:825).
  - Three-ID call: staging loads three rows (...:864); the upsert inserts three references (24 WAL records) and still deletes four prior rows through the anti-join (...:1441, ...:1447),
    yielding a 7 ms total run (...:1567).

  Issues

  - Returning false after an invalid reference still purges every reference for the parent; that is both a correctness risk and a large source of WAL/IO churn.
  - The anti-join delete fires on every call and scans the entire parent’s reference set even when only one alias changes, matching the heavy WAL totals seen during the load test.
  - Repeated key-share probes add FPIs and latency; they may be duplicating protection already provided by ON CONFLICT.
  - Every call rebuilds the staging temp table, incurring sorts and local writes that the connection pool immediately discards.

  Recommendations

  1. Move the invalid-alias check ahead of the upsert/delete so the function can immediately RETURN FALSE without touching dms.reference.
  2. If business rules allow, rely on INSERT … ON CONFLICT for concurrency and drop the explicit FOR KEY SHARE probes, or at least batch them to avoid per-row FPIs.
  3. Revisit the “delete all missing references” pattern—batched diffs (e.g., DELETE … USING temp_reference_stage) or incremental updates can avoid scanning/deleting the whole set every
     time.
  4. Keep pursuing the earlier temp-table change (persistent per-backend staging) so the expensive CREATE/TRUNCATE + branchy runtime partition pruning isn’t repeated on each pooled
     connection.

Next iteration:

InsertReferences

  - The CTE delete still performs an Append of 16 TID scans, so even a single parent document invalidation forces planner to probe every partition, costing ~2.5 ms of read I/O and rewriting
  two buffers (…_095909.log:2965). Rewriting this step to target the known partition (e.g. dynamic DELETE FROM ONLY dms.reference_%(partition)s) would avoid the cross-partition sweep.
  - Duplicate referential IDs hit the conflict filter correctly (Tuples Inserted: 0, Conflicting Tuples: 1 at /var/log/postgresql/postgresql-2025-10-31_095909.log:1897), but the full call
  still consumes 22.6 ms and touches 5.2 k shared buffers while writing 23 FPIs (…_095909.log:2081). The extra cost stems largely from the partition-spanning delete above and the key-share
  probes.
  - Invalid IDs short-circuit quickly: the new EXISTS check flags the staged null alias (…_095909.log:2266) and the function returns in 2.8 ms with only 129 shared hits (…_095909.log:2283).
  - Each call issues SELECT … FOR KEY SHARE against both dms.document and dms.alias, and these touches now generate small WAL writes (~0.3–0.45 ms each, 1–2 FPIs) when hint bits update the
  buffer (…_095909.log:2492, …_095909.log:2562). If the lock is only guarding concurrent writers from stepping on rows already held by the transaction, consider replacing it with SELECT …
  FOR SHARE SKIP LOCKED or reusing the lock taken during the alias lookup to cut the extra round trips.

  GetInvalidReferencesAndClear

  - The helper fails to create and to run because it references temp_reference_stage, which only exists inside InsertReferences; the CREATE attempt logs relation "temp_reference_stage" does
  not exist, and execution raises an ambiguous-column error (/var/log/postgresql/postgresql-2025-10-31_095909.log:1562, …_095909.log:1620). Wrap the lookup/cleanup in PL/pgSQL inside the
  original function (using the existing temp table), or persist the invalid references in a real unlogged table so the helper can operate.

  Recommendations

  - Narrow the DELETE step to the specific child partition—either dispatch to ONLY dms.reference_<partition> via dynamic SQL or add a generated partition key column in the staging table so
  the planner can prune during a simple DELETE … WHERE parentdocumentpartitionkey = … AND NOT EXISTS….
  - Optionally cache the alias/document locks pulled at the start of the upsert so you only touch each row once per call; it will shave the remaining 0.8–1 ms of WAL-heavy FOR KEY SHARE
  probes on hot parents.
  - Rework GetInvalidReferencesAndClear to operate in the same session context (or on an unlogged staging table) before wiring the loader to consume its output.



─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

• To stop the delete from fanning out across every partition, aim it straight at the one partition that matches the parent’s partition key. Because the function already knows
  p_parentDocumentPartitionKey, you can build a single-partition DELETE with dynamic SQL:

  DECLARE
      reference_partition text := format('dms.reference_%1$02s', p_parentDocumentPartitionKey);
  BEGIN
      ...
      EXECUTE format(
          $sql$
          DELETE FROM %s AS r
          WHERE r.parentdocumentid = $1
            AND NOT EXISTS (
                  SELECT 1
                  FROM temp_reference_stage AS s
                  WHERE s.aliasid = r.aliasid
                    AND s.referentialpartitionkey = r.referentialpartitionkey
            )
          $sql$, reference_partition
      )
      USING p_parentDocumentId;

      -- optional: remove staged rows here
  END;

  Key points:

  - format() builds the exact partition table name (reference_00, reference_01, …) that holds the parent’s rows, so PostgreSQL never instantiates the Append/TID scans across all 16
  partitions.
  - Keep the NOT EXISTS predicate; it now executes entirely inside the targeted partition, comparing only the staged aliases that belong to this request.


More refinement, this of the get invalid and delete:

  GetInvalidReferencesAndClear

  - The helper fails to create and to run because it references temp_reference_stage, which only exists inside InsertReferences; the CREATE attempt logs relation "temp_reference_stage" does
    not exist, and execution raises an ambiguous-column error (/var/log/postgresql/postgresql-2025-10-31_095909.log:1562, …_095909.log:1620). Wrap the lookup/cleanup in PL/pgSQL inside the
    original function (using the existing temp table), or persist the invalid references in a real unlogged table so the helper can operate.


------

After some improvements:

• InsertReferences Behavior (22:23 CDT tests)

  - Duplicate ID path (INSERT with 2 identical GUIDs) now runs in 9.68 ms with 2 831 shared-buffer hits, 0 reads, and ~5.7 KB WAL total (/var/log/postgresql/postgresql-2025-10-
    31_095909.log, around lines 4 880‑4 910). The INSERT … ON CONFLICT immediately hits the existing row (Tuples Inserted: 0, Conflicting Tuples: 1, 186 buffer hits) and the dynamic DELETE
    FROM dms.reference_00 clears 4 stale entries in 0.41 ms. Despite the dedupe, the parent partition scan still drags in ~2.8 k buffers—worth investigating further because it dominates the
    call time.
  - Three-ID path (3 distinct GUIDs) fell to 7.50 ms with 634 shared-buffer hits, a single shared read (28 µs), and 39 KB WAL (lines≈5 740-5 770). The staging insert is cheap (0.26 ms),
    the upsert writes 3 rows (23 WAL records, 9 FPIs), and the cleanup delete only touches 14 buffers. This is a big improvement over the earlier 45.9 ms / 3.1 k-hit plan you captured pre-
    change.
  - Invalid ID path (all GUIDs missing in Alias) now bails out in 3.26 ms with 142 hits, 4 reads (0.61 ms), and 7 KB WAL (lines≈5 000-5 120). The WITH staged insert writes the temp row, the
    EXISTS test spots aliasid IS NULL, and the function returns FALSE without touching dms.Reference. The temp row is left in temp_reference_stage, as expected for later inspection.

  GetInvalidReferencesAndClear

  - Calling SELECT * FROM dms.GetInvalidReferencesAndClear(11,0) from a new backend at 22:20 raised temp_reference_stage is not initialized for this session (lines≈4 520-4 535). Because
    the temp table is created per session inside InsertReferences, any follow-up query that lands on a different pooled connection will fail. With Npgsql pooling that failure is the common
    case, so the new diagnostic function is effectively unusable.

  Takeaways & Next Steps

  - The refactor shaved 15–38 ms off the “normal” paths and cut buffer churn by ~80 % there, but the duplicate path still burns ~2.8 k buffer hits. Expose that by adding RAISE NOTICE
    counters (only in staging) or instrumenting the branch to see which SQL is responsible, then consider collapsing the anti-join into an index-driven delete on just the conflicting alias
    rows.
  - Rework invalid-reference reporting so it survives connection pooling: either return the invalid UUIDs directly from InsertReferences (e.g., OUT parameter or RETURNS TABLE), or stage
    them in an unlogged per-backend table keyed by pg_backend_pid and fetch them within the same connection before releasing it.
  - Keep an eye on the FK check query SELECT 1 … FOR KEY SHARE (≈0.27 ms, 6 hits). If that came from an explicit addition, evaluate whether you can rely on the existing FK to avoid extra
    locking.
  - Once the invalid-reference path is fixed, rerun the load test and compare pg_stat_statements totals—especially for the duplicate workload—to verify buffer pressure stays low.

===
  Same scenario, but second ask:


• Log Review

  - Duplicate-ID call at /var/log/postgresql/postgresql-2025-10-31_095909.log:4880 ran in 9.67 ms with 2 830 shared-buffer hits; most time comes from the INSERT … ON CONFLICT DO UPDATE
    (0.41 ms) plus the FK enforcement scans (SELECT 1 … FOR KEY SHARE, 0.27 ms each) and the partition-local delete (0.41 ms). The stage load itself is cheap (<0.15 ms).
  - Three-unique-ID call at …log:5753 completed in 7.50 ms inserting three rows; the same FK checks appear but now the INSERT spends 2.53 ms doing real writes while the delete is 0.41 ms.
  - Invalid-ID probe at …log:5089 returned FALSE in 3.26 ms, leaving the bad UUID staged for inspection; only 142 shared hits were needed because we never touched the reference tables.
  - dms.GetInvalidReferencesAndClear is currently unusable across pooled sessions: /var/log/postgresql/postgresql-2025-10-31_095909.log:4533 shows it raising temp_reference_stage is not
    initialized for this session when the follow-up query lands on a different connection.

  Recommendations

  - Avoid the no-op update path on duplicates: instead of relying solely on INSERT … ON CONFLICT DO UPDATE, split the work into (a) INSERT … ON CONFLICT DO NOTHING for new aliases and (b)
    UPDATE dms.reference SET … FROM temp_reference_stage WHERE … AND row differs. Duplicate payloads that match existing rows will then bypass the FK FOR KEY SHARE probes entirely, dropping
    the duplicate scenario to the same ~7 ms as the happy path.
  - If you prefer to stay declarative, a MERGE INTO dms.reference (PostgreSQL 15+) with separate WHEN MATCHED AND … THEN UPDATE / WHEN NOT MATCHED THEN INSERT clauses achieves the same
    effect while still targeting a single partition (use MERGE INTO dms.reference_<pp> via EXECUTE).
  - Retire dms.GetInvalidReferencesAndClear and surface the invalid UUIDs directly from dms.InsertReferences: change the signature to return both success boolean and invalid_ids uuid[],
    populate invalid_ids := ARRAY(SELECT … WHERE aliasid IS NULL), and clear the stage in the same function. Callers get the IDs in the same round-trip, and the 99 % happy path still just
    sees a fast TRUE/empty array.
      1. If changing the signature is impossible, stash invalid IDs into an unlogged helper table keyed by pg_backend_pid() inside InsertReferences and have GetInvalidReferencesAndClear
         query/clear that table; this keeps the data available across pooled sessions without depending on temp-table state.
  - Auto-explain overhead is visible in the totals; once you finish tuning, raise auto_explain.log_min_duration back toward production levels to avoid the extra latency you’re currently
    measuring.

  Next Steps

  1. Prototype the split INSERT/UPDATE (or MERGE) and rerun the duplicate test to confirm the FK probes disappear.
  2. Update the API contract so InsertReferences surfaces invalid IDs directly; remove the failing helper once callers are migrated.

  ## Update - 2025-11-01-00-37 (After lots of tuning)


 Key Findings

  - After the required 10‑minute soak, pg_stat_statements showed SELECT success, invalid_ids FROM dms.InsertReferences($1,$2,$3,$4) climbing from 731 820 to 785 237 calls in 60 s (~53 k calls/
    min). Each call averages 2.58 ms, touches ~248 shared buffers (~2 MB) and emits ~7.3 KB of WAL, totaling ~4.1 GB WAL and keeping CPU and buffer churn high.
  - Active backends repeatedly block on WAL durability: pg_stat_activity reported WalSync/WALWrite wait events, while pg_stat_io logged 5 800 650 client WAL writes with 126 s write time and
    1 935 s fsync time since the last reset—consistent with synchronous_commit=on forcing per-transaction flushes even though iostat showed the NVMe device only ~46 % busy with ~0.1 ms write
    latency.
  - The upsert pipeline around InsertReferences adds further churn: DELETE FROM dms.Document … executed 1.09 M times (0.75 ms avg, 328 MB WAL) and connection resets issued DISCARD TEMP 2.68 M
    times (385 s total), so every pool checkout recreates/drops temp state and amplifies buffer activity.
  - The DMS service (EdFi.DataManagementService, pid 171969) consumes ~250 % CPU with negligible I/O, indicating the bottleneck sits in the database layer; autovacuum briefly hit 100 % CPU but
    no blocking locks were observed.
  - The Python load generator (pid 175522) uses ~80 % of a single core and ~22 KB/s write throughput (pidstat), so it is not throttling the test.

  Supporting Data

  - pg_stat_statements: SELECT success, invalid_ids … — 785 237 calls, 2.58 ms mean, 4.09 GB WAL, 143 M buffer hits (edfi_datamanagementservice).
  - Aggregated view (custom query): scalar vs. returning call variants both average ~248 shared hits and ~7.27 KB WAL per call.
  - pg_stat_activity: 2 sessions on WALWrite, 1 on WalSync, confirming commit stalls.
  - pg_stat_io: client backend | wal | normal — writes = 5 800 650, write_time = 126 422 ms, fsync_time = 1 935 327 ms.
  - iostat -x 1 3: nvme1n1 ~45 MB/s read, ~48 MB/s write, 0.10 ms w_await, 46 % util.
  - pidstat -u/-d: Python load (pid 175522) ~80 % CPU, negligible I/O; DMS service ~250 % CPU, negligible I/O.

  Next Steps

  1. If the load test can trade durability for throughput, run with SET LOCAL synchronous_commit = 'local' (or off) to eliminate per-transaction WalSync waits; alternatively batch commits
     within the load tool. Re-test to confirm latency gains.
  2. Review InsertReferences’ delete/refresh logic: consider keeping a session-persistent staging structure (avoid DISCARD TEMP churn), or redesign the “remove missing references” step to rely
     on indexed keys only, cutting the ~248 buffer touches per call.
  3. Profile connection-pool usage in the DMS service; reducing the frequency of full pool resets (DISCARD TEMP, RESET ALL) will lower CPU/WAL overhead and improve InsertReferences latency.


**** Suggestions after followup:

• InsertReferences is the dominant write path in this workload, so tuning it pays off quickly. Here’s what the monitoring shows, followed by concrete changes to the function definition
  (dms.insertreferences, see \sf+ dms.insertreferences lines 26‑134).

  What the metrics say

  - pg_stat_statements → 1.02 M scalar calls at 2.50 ms mean plus 0.79 M “SELECT success…” callers at 2.58 ms, each touching ~248 shared buffers (~2 MB) and writing ~7.3 KB of WAL; that’s ~4 GB WAL
    for InsertReferences alone during the sample window.
  - Wait profile → backends frequently sit on WALWrite/WalSync waits, so every extra write you avoid immediately helps commit latency.
  - The upsert + prune block (lines 69‑123) runs on every call, even when the reference set is unchanged, so we still emit WAL/dirty buffers even when nothing needs to change.

  Targeted tuning suggestions

  - Skip the heavy upsert when nothing changed (dms.insertreferences:69-123): before the INSERT … ON CONFLICT, join the staged rows against the existing partitioned table and exit early when the
    set of aliases/targets already matches. A lightweight probe (e.g., SELECT bool_and(...) or EXCEPT on (aliasid, referentialpartitionkey, referenceddocumentid, referenceddocumentpartitionkey)) can
    return quickly because the unique index on (parentdocumentpartitionkey,parentdocumentid,aliasid) is selective. When the set is unchanged, avoid both the INSERT … ON CONFLICT DO UPDATE and the
    dynamic DELETE, eliminating ≈7 KB of WAL and ~248 buffer touches per call.

  Follow-up monitoring

  After implementing the above, keep an eye on pg_stat_statements for the two InsertReferences entries: mean execution time should drop, the per-call WAL volume should fall sharply, and the shared-
  blk-hit metric should approach double digits. Also confirm in pg_stat_activity that WalSync waits disappear under the same load profile.

  Let me know when you’re ready to validate the revised function and we can script the changes.


Additional info on skipping upsert if no changes:

• Skipping the insert/delete cycle is attractive—the current pattern at src/dms/backend/EdFi.DataManagementService.Backend.Postgresql/Deploy/Scripts/0010_Create_Insert_References_Procedure.sql:73-
  130 keeps hammering INSERT … ON CONFLICT plus the dynamic partition delete even when the incoming snapshot already matches the table. A fast equality probe that fans out through the selective
  ux_reference_parent_alias index could avoid ≈7 KB of WAL and buffer churn in the ~25 % “no-op” scenario.

  Key considerations before adopting it:

  - The probe must be symmetric. You need to detect both “stage row missing in table” and “table row missing in stage”; an EXISTS/NOT EXISTS pair on (AliasId, ReferentialPartitionKey,
    ReferencedDocumentId, ReferencedDocumentPartitionKey) is cheaper than an EXCEPT (which sorts) and keeps everything index-driven.
  - Run the probe only after invalid_ids is empty. You can reuse temp_reference_stage—filter to aliasid IS NOT NULL and join to dms.Reference, letting partition pruning limit the scan to the one
    partition. That keeps it to one additional index lookup per staged alias.
  - If the probe finds the sets identical, short-circuit before the INSERT … ON CONFLICT and before the dynamic DELETE. You still return the success flag, and you leave the temp table in place for
    the return clause.
  - Concurrency remains safe under READ COMMITTED: the probe sees a fresh snapshot, so any genuine divergence forces the function down the existing write path. You just lose the side effect of
    rewriting rows when nothing changed—which is the intent.
  - Net win hinges on workload shape. For the 75 % of calls where something does change, you pay for the extra probe plus the original work. Benchmark with representative alias counts; if parents
    commonly carry only a handful of rows, the added SELECT cost is negligible, but if they average hundreds, the extra scan could erase the benefit.

  Implementation sketch (inside the existing IF cardinality(invalid_ids) = 0 THEN block):

  IF NOT EXISTS (
      SELECT 1
      FROM temp_reference_stage s
      LEFT JOIN dms.Reference r
        ON r.ParentDocumentPartitionKey = s.parentdocumentpartitionkey
       AND r.ParentDocumentId = s.parentdocumentid
       AND r.AliasId = s.aliasid
      WHERE s.aliasid IS NOT NULL
        AND (
          r.AliasId IS NULL OR
          r.ReferentialPartitionKey IS DISTINCT FROM s.referentialpartitionkey OR
          r.ReferencedDocumentId IS DISTINCT FROM s.referenceddocumentid OR
          r.ReferencedDocumentPartitionKey IS DISTINCT FROM s.referenceddocumentpartitionkey
        )
  )
  AND NOT EXISTS (
      SELECT 1
      FROM dms.Reference r
      WHERE r.ParentDocumentPartitionKey = p_parentDocumentPartitionKey
        AND r.ParentDocumentId = p_parentDocumentId
        AND NOT EXISTS (
            SELECT 1
            FROM temp_reference_stage s
            WHERE s.aliasid = r.AliasId
              AND s.referentialpartitionkey = r.ReferentialPartitionKey
              AND s.referenceddocumentid = r.ReferencedDocumentId
              AND s.referenceddocumentpartitionkey = r.ReferencedDocumentPartitionKey
        )
  )
  THEN
      RETURN QUERY SELECT TRUE, ARRAY[]::uuid[];
      RETURN;
  END IF;

  If microbenchmarks confirm the no-op rate and alias counts you quoted, this early-exit pays for itself; just measure the added probe cost under load before committing.



## Update - 2025-11-01-23-04 (permanent unlogged staging table, dedup in C#, pure insert hint) Best perf with References so far - 6.5ms avg, 7ms median

• Database Findings

  - WAL flushes dominate wait time: pg_stat_io shows client backends issued 1 255 650 WAL writes with 25 042 ms write_time and 427 519 ms fsync_time; pg_stat_activity frequently reports IO/WalWrite waits during COMMIT,
    confirming a WAL-bound workload.
  - synchronous_commit=on and 11 M commits since the last reset (pg_stat_database) mean almost every tiny transaction forces its own flush, so group commit rarely helps.
  - Checkpoints are frequent and heavy: checkpoint_timeout is 5 min while pg_stat_checkpointer reports 1 089 510 ms of checkpoint write_time since 19:52, amplifying WAL pressure.
  - Shared buffers are recycling effectively (1.6 B hits vs. 15.8 M reads), so the bottleneck isn’t data-page IO but log durability.

  InsertReferences Metrics

  - pg_stat_statements shows 757 792 calls, 1.76 ms mean execution, and 1.13 GB total WAL → ~1.78 KB per call; the function itself is CPU-light and buffer-resident.
  - For comparison, the INSERT into dms.Document produces ~3.38 KB WAL per call, so downstream document churn is the larger WAL producer in this code path.
  - The equality probe exercises dms.ix_referencestage_parent heavily: 3.88 M index scans with 10.1 M tuple fetches, confirming the fast-path predicate is working; dms.ReferenceStage currently holds 143 k dead tuples
    without any recorded vacuum (pg_stat_all_tables), so plan periodic maintenance.
  - Partition indexes (dms.reference_##_referentialpartitionkey_aliasid_idx) see ~2.4 M scans each, matching the expected selective lookups and validating the unlogged staging design.

  System & Application

  - The python load harness (pid 69808) runs at ~85 % CPU and 0.1 % memory with default nice level; on this 24-core host it doesn’t contend with Postgres, so the generator itself isn’t the test bottleneck.
  - The DMS frontend (EdFi.DataManagementService.Frontend.AspNetCore, pid 69211) stays around 200 % CPU and ~1 GB RSS; plenty of headroom remains, but watch swap usage (3.3 GB in use) if more services join the run.
  - Disk service time is low (nvme1n1 w_await ≈ 0.11 ms, 37.9 % util via iostat), reinforcing that the delay is log fsync latency, not media saturation.
  - App logs record repeated 401s when fetching authorization metadata (src/dms/frontend/EdFi.DataManagementService.Frontend.AspNetCore/logs/20251101.log:27), which can add upstream latency and extra DB retries;
    resolve the CMS auth issue to slim per-request work.

  Next Steps

  1. Reduce WAL flush contention: batch multiple API mutations into a single transaction where safe, or run Idempotent/high-volume paths with SET LOCAL synchronous_commit='local'/'off' to let group commit absorb the
     fsync.
  2. Relax checkpoint cadence (e.g., raise checkpoint_timeout to 15 min and keep checkpoint_completion_target ≥ 0.9) so checkpoints stop crowding the WAL writer during peaks.
  3. Keep the new staging table lean with a scheduled VACUUM (ANALYZE) dms.ReferenceStage or periodic TRUNCATE, or enable autovacuum aggressively, to prevent stats drift as dead tuples accumulate.
  4. Fix the CMS authorization failures so the frontend stops issuing failing HTTP calls, and consider tagging the connection string with an ApplicationName to make future pg_stat_activity attribution easier.

  Let me know if you’d like help applying any of these changes or digging deeper into DMS-side timings.

 ### I then asked about fast-path percentages

 • Fast-path calls are the minority. Using pg_stat_statements totals captured during the run:

  - dms.InsertReferences executed 1 377 552 times.
  - Every new document upsert issues a companion INSERT INTO dms.Document … (query id -8359663333965759041), and we logged 961 806 of those during the same interval.

  Because a brand-new document can’t qualify for the fast-path (it has no existing reference state), at least those 961 806 InsertReferences invocations had to take the full write path.
  That already accounts for ≈70 % of all calls (961 806 / 1 377 552 ≈ 0.698). The remaining ≈30 % of calls are the only ones that could even have short‑circuited.

  Two observations push the actual percentage lower than that ceiling:

  - We also saw 417 504 document updates (query id 8463487787006168343) and 960 311 document deletes (-5488951830561609739). Any update that changed the reference set, or any delete that
    required cleanup, would have forced the heavy branch too.
  - The function’s own WAL footprint averaged ~1.78 KB per call, which aligns with the cost of running the upsert/delete path most of the time; a true fast-path call would be near zero WAL.

  Putting it together: roughly 25–30 % of the InsertReferences executions were able to short‑circuit, with the rest performing actual reference writes. To get exact accounting, we’d need to
  flip pg_stat_statements.track to all (so the nested INSERT/DELETE inside the function are counted) or add lightweight instrumentation in the function itself.

### I then asked about further pure insert optimizations

• A few more levers remain for the “brand-new document + pure insert” case beyond the current p_isPureInsert delete skip:

  - Skip the equality probe entirely when p_isPureInsert is true. For a fresh parent there cannot be existing rows, so the probe only burns CPU on ux_reference_parent_alias. Short-circuit
    the branch before the fast-path NOT EXISTS checks.
  - Bypass the staging table for this branch. You still need the alias lookups and invalid-ID aggregation, but you can keep it in a single CTE:
      1. WITH staged AS (SELECT … FROM unnest … LEFT JOIN dms.Alias …) – identical to today but not persisted.
      2. SELECT array_agg(...) INTO invalid_ids FROM staged WHERE aliasid IS NULL;
      3. If invalid_ids is empty, run a plain INSERT INTO dms.Reference … SELECT … FROM staged WHERE aliasid IS NOT NULL;

    Because you never touch dms.ReferenceStage, there’s no DELETE/INSERT on the unlogged table and no follow-up cleanup per call.
  - Use a conflict-free insert when p_isPureInsert. In that branch swap the INSERT … ON CONFLICT DO UPDATE for either a straight INSERT (fastest) or INSERT … ON CONFLICT DO NOTHING. Since a
    new parent shouldn’t have any references yet, that avoids the per-row conflict check and the EXCLUDED comparison entirely.
  - Optionally add light deduping inside the CTE (e.g., SELECT DISTINCT ON (referentialid, referentialpartitionkey) …) to protect against accidental duplicates without relying on ON
    CONFLICT.

  Together these changes remove staging I/O, equality probe lookups, and conflict handling from the pure insert hot path, leaving only the alias join plus a single insert. If you want
  concrete code, I can sketch the CTE-based branch.


### I then asked about WAL write breakdown

• WAL Breakdown (current pg_stat_statements snapshot)

  - INSERT … INTO dms.Document … (queryid -8359663333965759041): 3 292 141 836 bytes over 961 806 calls → ≈3.38 KB per call.
  - SELECT success, invalid_ids FROM dms.InsertReferences … (queryid -7737659587446346593): 2 462 604 404 bytes over 1 377 552 calls → ≈1.78 KB per call.

  So, looking just at these two statements, Document inserts account for ~57% of the combined WAL (3.29 GB / (3.29 GB + 2.46 GB)), with InsertReferences contributing the remaining ~43%. On
  a per-call basis, each document insert writes almost twice as much WAL as a reference insert because it touches the primary key, partition index, JSONB payload, and audit columns.

  If we expand the lens to the other hot statements we measured:

  - Document deletes (queryid -5488951830561609739): 304 M WAL over 960 311 calls (~317 B/call).
  - Document updates (8463487787006168343): 790 M WAL over 417 504 calls (~1.89 KB/call).

  Stacking those together shows that the document table is the dominant WAL emitter across the workload—roughly 4.39 GB versus 2.46 GB for references alone—so any reductions in document
  insert/update churn (larger batches, fewer redundant updates, lighter JSON payload writes) will have the biggest impact on overall WAL write pressure.

### I then asked why updates were a lot less than inserts

• Even though each update rewrites the JSONB payload, PostgreSQL can treat most of those UPDATE dms.Document ... statements as HOT updates: the primary key and other indexed columns stay
  unchanged, so the engine simply appends a new tuple version on the same heap page, marks the old version dead, and leaves all index entries untouched. That cuts the WAL volume to roughly
  “heap tuple only,” averaging the 1.89 KB/call we observed (790 MB ÷ 417 504 calls). By contrast, an INSERT must log the full heap tuple plus every new index entry on the row, emits
  visibility-map changes, and often includes full-page images when extending new pages after checkpoints. That extra index churn and page initialization explains why inserts are about
  3.38 KB/call (3.29 GB ÷ 961 806), nearly double the update cost despite the JSONB rewrite.


### I then asked about getting the insert size down

• A few levers can shave real WAL off each dms.Document insert:

  - Reduce full-page images. After every checkpoint, the first change to a heap or index page emits an 8 KB FPI. Raise checkpoint_timeout (and keep checkpoint_completion_target high) so
    checkpoints aren’t hammering every 5 min, and be sure wal_compression = on so the FPIs that do fire are compressed.
  - Trim index footprint. Every maintained index adds its own WAL records. Audit the current index set on dms.Document; if any are rarely used or could be converted to partial/covering
    designs, removing them lowers insert WAL directly.
  - Keep hot pages hot. Inserts that extend the table hit new pages (and thus FPIs). Lowering fillfactor isn’t helpful for inserts, but pre-warming via larger batches per transaction can
    let multiple tuples share a page before the next checkpoint. Alternatively, consider staging bulk loads into an UNLOGGED table and merging, if durability requirements allow.
  - Shrink the tuple. Any reduction in the JSONB payload or other wide columns (e.g., trimming metadata, compressing external blobs) lowers the heap tuple size and consequently the WAL
    record for both heap and associated TOAST/index entries.
  - Only necessary writes. Double-check the insert path for redundant columns (e.g., default timestamps, trace IDs) that may be set later via updates. Deferring or eliminating them during
    the insert keeps the tuple smaller.

  Combining less frequent checkpoints, compressed FPIs, and leaner indexing typically has the biggest effect on per-insert WAL without sacrificing correctness. If you’d like, I can help
  profile the current index set or test the impact of adjusting checkpoint/WAL settings on a staging instance.


### I then asked about C#-side optimizations for queries

• Wal-Specific Opportunities

  - PostgresqlDocumentStoreRepository.UpsertDocument (src/dms/backend/EdFi.DataManagementService.Backend.Postgresql/PostgresqlDocumentStoreRepository.cs:29) and UpdateDocumentById (:87) open a fresh connection,
    start a transaction, perform the write, then commit. Every failure path still makes it all the way through InsertDocumentAndAlias (SqlAction.cs:285) or UpdateDocumentEdfiDoc (SqlAction.cs:318) before
    discovering invalid references; even though the caller rolls the transaction back, PostgreSQL has already emitted full WAL for the insert/update. You can trim that by validating references first: build a
    lightweight helper (e.g. SELECT referentialId FROM unnest(...) LEFT JOIN dms.Alias … WHERE alias.Id IS NULL) and call it before you touch dms.Document or dms.Alias. If it returns anything, bail early. On the
    insert path that short-circuits everything before InsertDocumentAndAlias; on the update path it keeps _sqlAction.UpdateDocumentEdfiDoc (called in both UpsertDocument.AsUpdate and UpdateDocumentById.UpdateById)
    from rewriting the JSONB row only to be rolled back.
  - For brand-new documents you already pass IsPureInsert: true into dms.InsertReferences. Once the database side has the “pure insert” branch that skips staging/equality probes, mirror that in the repo by
    skipping the equality probe entirely when upsertRequest.DocumentInfo.DocumentReferences resolves to an empty existing set. That keeps the pure-path call down to just one heap insert and one index update
    instead of the extra probe traffic.
  - Make sure new document UUIDs aren’t random v4s. The unique index on (DocumentPartitionKey, DocumentUuid) (see 0001_Create_Document_Table.sql:23) and on alias (ReferentialPartitionKey, ReferentialId) (0002_…
    sql:22) both suffer page splits with random UUIDs; switching API-side generation to sequential GUIDs (UUID v7 or SQL Server–style combs) keeps insertions append-only within each partition, which lowers index
    churn and the accompanying WAL.
  - Keep connection pool resets cheap. pg_stat_statements shows each call running SET SESSION AUTHORIZATION, RESET ALL, etc. If you can enable NoResetOnClose=true in the connection string (and you don’t rely on
    session GUCs), you eliminate a handful of catalog writes per request. It doesn’t move WAL much, but it shaves a few statements off every POST/PUT and keeps headroom for the main workload.

  Applying the “validate-first” change will give you the most immediate WAL drop: bad reference payloads go straight to an error without touching heap/index pages. Layering optional synchronous_commit tuning and
  sequential GUIDs on top of the database-side fast path will squeeze the per-request log volume even more while staying within the current POST/PUT semantics.


## Update - 2025-11-02-16-58 (Check early for invalid references, Npgsql no reset)

• Bottlenecks

  - WAL flush contention is still the primary throttle: since the reset (pg_stat_wal, 2025‑11‑02 16:57) Postgres emitted 27 M records/8.4 GB WAL, with client backends forcing 902 690
    synchronous WAL writes totaling 20.5 s write time and 313.9 s fsync (pg_stat_io). pg_stat_activity continues to show IO/WalWrite wait events during commits.
  - dms.InsertReferences remains the dominant SQL hotspot: 596 484 calls at 1.66 ms mean, 1.04 GB WAL (≈1.75 KB/call) and 101 M buffer hits (pg_stat_statements). Function stats confirm
    986 s spent inside the routine (pg_stat_user_functions), so the database is busy but not slow per-call—latency comes from log durability.
  - Downstream document churn amplifies WAL pressure: the partitioned INSERT INTO dms.Reference call (queryid 6070861028664210120) burns another 1.03 GB WAL over 562 k invocations, and the
    paired DELETE FROM dms.Document issues 129 MB WAL at 0.72 ms/call. These add ~2.8 KB WAL per request on top of InsertReferences.
  - Autovacuum is working hard to keep up with delete churn: a worker is currently the #2 CPU consumer, and pg_stat_all_tables shows each reference partition holding ~20–26 k dead tuples
    with 23–30 autovacuum runs since the reset. dms.ReferenceStage still accumulates ~118 k dead rows between purges, so continue scheduling aggressive vacuum/truncate to avoid catalog
    bloat.
  - Application-level behavior can add latency spikes: multiple sessions are “idle in transaction” holding FOR NO KEY UPDATE locks (pg_stat_activity), and the API logs still show
    authorization call failures (src/dms/frontend/EdFi.DataManagementService.Frontend.AspNetCore/logs/20251101.log:27), which trigger retries and extra DB work.

  System & Load Generator

  - The python load script (pid 255728) runs ≈92 % CPU, 0.1 % memory, nice 0: it isn’t resource-starving Postgres, and there’s ample idle CPU (top shows 58 % idle).
  - The DMS frontend process (pid 255084) is steady at ~260 % CPU and <1 GB RSS, so it’s not the bottleneck, but address the lingering CMS 401 errors to prevent additional request churn.
  - Disk latency remains low (NVMe w_await ≈0.1 ms via iostat), confirming the slowdown is commit/fsync pacing, not raw IO bandwidth.

  Recommendations

  1. Reduce per-transaction WAL flushes: batch multiple logical operations inside a single transaction where safe, or tag idempotent paths with SET LOCAL synchronous_commit = 'local'/'off'
     so group commit can absorb fsync latency.
  2. Tame checkpoint pressure: lengthen checkpoint_timeout (e.g., 15 min) and keep checkpoint_completion_target ≥0.9 so checkpoints don’t pile onto peak WAL activity.
  3. Keep the new staging table leaner: add a lightweight job to VACUUM (ANALYZE) or TRUNCATE dms.ReferenceStage between runs; it’s unlogged so this is cheap.
  4. Eliminate “idle in transaction” holders—close connections promptly after each request—and fix CMS authorization failures to avoid extra retries.
  5. Monitor WAL volume after these changes (reset stats, rerun load) to verify per-call WAL drops; if not, consider raising wal_buffers and lowering wal_writer_delay to 10 ms to smooth
     bursts.

### Brad's own notes

WAL writes for document inserts dropped from 3.4KB/call to 2.8KB/call.
WAL writes for reference inserts steady at 1.75KB/call (down from a pre-tuning 5-7KB/call)

### I gave it my postgresql.conf and asked for suggestions - did all but group commit (ignored durability)

• WAL-Focused Tweaks

  - ~/Downloads/temp/2025-11-02-16-58-postgresql.conf:252 – explicitly set wal_buffers = 128MB. The default auto value (~16 MB for 16 GB shared buffers) is small for your current
    8 GB+/10 min WAL volume; raising it lowers pressure on the WAL insertion locks and reduces partial flushes under bursty inserts.
  - ~/Downloads/temp/2025-11-02-16-58-postgresql.conf:254 – drop wal_writer_delay from 20 ms to 5–10 ms. A faster background writer keeps the log file nearly up‑to‑date so foreground
    commits have less to flush.
  - ~/Downloads/temp/2025-11-02-16-58-postgresql.conf:255 – un-comment and tighten wal_writer_flush_after = 256kB. This makes the writer push out smaller chunks whenever the log grows
    quickly, again shrinking the residual work each commit must fsync.
  - ~/Downloads/temp/2025-11-02-16-58-postgresql.conf:267-268 – grow max_wal_size to 32GB (and optionally min_wal_size to 8GB). Your workload already generates 8 GB between resets; giving
    the checkpointer more headroom prevents forced checkpoints that pile onto WAL writes.
  - ~/Downloads/temp/2025-11-02-16-58-postgresql.conf:258-259 – if you want to encourage group commit, enable a modest commit_delay = 50 (µs) with commit_siblings = 20. At your concurrency
    this lets each backend wait a hair for peers, increasing the odds that the shared flush done by walwriter covers several commits.
  - ~/Downloads/temp/2025-11-02-16-58-postgresql.conf:236 – optional but impactful: if the durability SLA allows, switch synchronous_commit = local. That keeps WAL durable on the local OS
    cache but lets PostgreSQL return immediately, leaving the kernel/fsync to complete in the background. Apply per role/transaction if only parts of the workload are latency sensitive.

  Reload with SELECT pg_reload_conf(); after editing (or restart if you change wal_buffers). Monitor pg_stat_io and pg_stat_wal on the next run; you should see fewer IO/WalWrite waits and
  lower per-commit fsync_time.


## Update - 2025-11-02-21-20 (Zstd WAL compression, other tunings as above)

• Findings

  - dms.InsertReferences still dominates DB time post-reset: 962 278 calls at 1.57 ms average, 1.77 KB WAL per call, and 149 M shared-buffer hits (pg_stat_statements
    queryid -7737659587446346593). The companion INSERT INTO dms.Reference adds 1.86 KB WAL per call, so each logical request still emits ≈3.6 KB of WAL despite zstd compression.
  - WAL flush latency remains the primary bottleneck. pg_stat_io shows client backends performed 1 151 647 WAL writes with 20.7 s write_time and 450.9 s fsync_time since the reset (stats at
    2025‑11‑02 21:52:40). Active sessions continue to wait on WalSync/WALWrite (pg_stat_activity), so synchronous commits are gating throughput.
  - Autovacuum is busy keeping partitions clean: an autovac worker is currently vacuuming dms.document_12, and every dms.Reference_## partition has 30–41 autovac runs with 12–38 k dead
    tuples remaining (pg_stat_all_tables). The unlogged stage table accumulated 14 M insert/delete cycles with 128 k dead rows and 20 M index probes (same view), indicating the probe path
    is hot.
  - System resources are not saturated: CPU still shows ~35 % idle (top), NVMe write latency is ~0.1 ms with ~38 % utilization (iostat), and the two python load generators together consume
    ≈150 % CPU without starving Postgres. Swap is nearly exhausted (8 GB allocated, ≈0 MB free), which is worth monitoring even though no immediate contention appears.
  - The DMS frontend process runs near 380 % CPU with ~1 GB RSS but reports only normal restarts and no recent errors (src/dms/frontend/EdFi.DataManagementService.Frontend.AspNetCore/
    logs/20251102.log:1-20).

  Recommendations

  1. Continue attacking WAL flush pressure: batch mutations into fewer transactions where possible, or use SET LOCAL synchronous_commit = 'local'/'off' on idempotent operations so group
     commit can absorb the 450 s fsync burden.
  2. Spread out checkpoint/flush work: ensure the recent postgresql.conf tuning kept checkpoint_timeout high and consider trimming wal_writer_delay to 10 ms so the WAL writer pre-flushes
     more aggressively.
  3. Keep dms.ReferenceStage tidy—schedule VACUUM (ANALYZE) or TRUNCATE between runs to reclaim the 128 k dead rows and maintain planner stats for the equality probe.
  4. Eliminate “idle in transaction” holders in the application so they don’t pin locks or inflate autovac workload; close or reuse connections promptly.
  5. Watch memory pressure: with swap nearly maxed, consider freeing other workloads or increasing RAM/swap to avoid future OS reclamation stalls during the test harness.

### Brad's own notes

WAL writes for document inserts dropped from 2.8KB/call to 1.86KB/call.
WAL write for reference inserts steady at 1.77KB/call

### I gave it my postgresql.conf and asked for suggestions

• Key Observations

  - High WAL pressure remains despite zstd compression. Client backends still perform synchronous WAL flushes on every commit; the config leaves synchronous_commit default on and doesn’t
    encourage group commit.
  - Aggressive autovacuum settings (high worker slots, low scale factor, no cost delay) keep tables clean but drive heavy CPU/WAL activity exactly when the load test peaks.
  - Memory knobs (16 GB shared_buffers, 64 MB work_mem, 2 GB maintenance_work_mem) are generous; combined with ~100 connections they explain the sustained swap exhaustion during tests.

  Suggested Tuning (~/Downloads/temp/2025-11-02-21-20-postgresql.conf)

  - Encourage group commit – add commit_delay = 1000 and keep commit_siblings = 5 just below the WAL section (~line 240). This queues commits for 1 ms when five or more siblings are active,
    increasing the chance of shared WAL flushes.
  - Trim work_mem – drop work_mem from 64 MB to 16–32 MB near the memory block (~line 120). With 20–30 concurrent sessions, the current setting can reserve several GB per complex query and
    pushes the system into swap.
  - Spread WAL writer effort – keep wal_writer_delay = 5ms but raise wal_writer_flush_after to 1MB (same section) so the writer amortizes writes better while still flushing frequently.
  - Leverage fast storage – explicitly set effective_io_concurrency = 256 and maintenance_io_concurrency = 256 in the I/O section (~line 210) to let PostgreSQL exploit NVMe queue depth.
  - Control autovacuum churn – set autovacuum_vacuum_cost_delay = 5ms and leave autovacuum_vacuum_cost_limit = 1000 in the autovacuum block (~line 700). This keeps workers active but yields
    briefly between bursts, smoothing their WAL and CPU impact.
  - Optional durability relaxation – if the workload can tolerate it, change default synchronous_commit to local in the WAL section (~line 230) and let critical transactions override it to
    on. This retains crash safety but removes per-transaction fsync waits.
  - IO method – on kernels with io_uring support, consider io_method = io_uring and a small io_workers pool (e.g., 4) in the I/O block (~line 205) to reduce backend flush latency.

### Deeper analysis:

• - While the run was active we sampled pg_stat_activity and saw 22 concurrent backends tied to edfi_datamanagementservice; after the load ended the view now shows a single remaining
    session, but 22 is the practical peak during the test.
  - From pg_stat_io (client backend / wal / normal) the full run accumulated 2 836 529 WAL writes with 942 695 ms of fsync time, which works out to roughly 0.33 ms of fsync wait per flush
    on average—so WAL flushes did queue, but only for a third of a millisecond each.

### Revised tweak recommendations:

• Given the latest data—roughly 22 concurrent sessions and ~2.8 M WAL flushes averaging 0.33 ms each—the configuration looks generally healthy, and keeping synchronous_commit = on is fine.
  I’d keep most of the earlier recommendations, with a couple of tweaks:

  - Encourage group commit without sacrificing durability
    Add commit_delay = 1000 and leave commit_siblings = 5. With 20+ simultaneous backends this nudges commits to batch for a single fsync while honoring synchronous durability.
  - WAL writer smoothing
    Leave wal_writer_delay = 5ms, but raise wal_writer_flush_after = '1MB'. That lets the background writer coalesce more WAL before flushing, reducing the per-commit flush pressure that
    still shows up in waits.
  - I/O concurrency
    The NVMe throughput is barely tapped, so explicitly set effective_io_concurrency = 256 and maintenance_io_concurrency = 256. This helps the planner issue deeper asynchronous reads
    during heavy work (vacuum, certain queries).
  - Autovacuum pacing
    Keep the aggressive thresholds, but add autovacuum_vacuum_cost_delay = 5ms. That prevents autovac workers from hammering WAL writes when the load test peaks, while still allowing them
    to run frequently.
  - work_mem
    Since swap usage mostly comes from other tooling, leaving it at 64 MB is acceptable. If you ever see Postgres backends swapping under load, the first knob to turn down would still be
    work_mem, but otherwise no change is required.

  - Brad note: also enable io_uring

  No other adjustments are warranted based on the new wait-profile; the existing zstd compression and 128 MB wal_buffers are appropriate. After applying these, reload the config and keep an
  eye on pg_stat_io to confirm fsync time per flush stays in the same range or improves.


### Stats

  | Metric                | Value                       |
  |-----------------------|-----------------------------|
  | Total Requests        | 2,167,991                   |
  | Total Failures        | 1,473 (0.068% failure rate) |
  | Throughput            | 1,204.79 req/s              |
  | Median Response Time  | 7ms                         |
  | Average Response Time | 7.38ms                      |
  | Min Response Time     | 1ms                         |
  | Max Response Time     | 374ms                       |

  Percentile Response Times

  - 50th (Median): 7ms
  - 95th Percentile: 12ms ✅ (SLA standard)
  - 99th Percentile: 17ms ✅ (Excellent tail latency)
  - 99.99th Percentile: 62ms


## Update - 2025-11-03-11-06-group-commit-tuning (Added group commit, other tunings as above but not io_uring)

• Database

  - InsertReferences remains the hot spot with 343 k calls at 1.66 ms mean and ~1.76 KB WAL per call; the coupled INSERT INTO dms.Reference adds ~1.84 KB WAL, so each logical request still
    emits ≈3.6 KB (via pg_stat_statements queryids -7737659587446346593 and 6070861028664210120).
  - Group-commit tuning lowered pressure but WAL syncs still gate throughput: client backends flushed 432 126 WAL writes for 10.2 s write_time and 176.5 s fsync_time (since
    2025‑11‑03 11:25:19 reset), and live sessions still report IO/WalSync/WALWrite waits during COMMIT.
  - Autovacuum is active on dms.document_01, and dms.ReferenceStage has cycled 20.7 M rows with 79 k dead tuples, showing the equality probe path stays hot; it was last vacuumed at
    11:33:33.
  - Database I/O remains buffer-resident (35 M reads vs. 3.5 B hits) with no data-file write waits, so commit durability is the remaining bottleneck.

  System & Load

  - The Ed-Fi frontend (pid 443309) runs near 120 % CPU with ~1 GB RSS and shows only normal restarts (src/dms/frontend/EdFi.DataManagementService.Frontend.AspNetCore/logs/20251103.log:1-
    5).
  - The load generator (pid 464160) consumes ~78 % CPU but stays well below host capacity (24 cores), so it isn’t throttling the test; note the separate borg check backup (pid 473721) using
    ~88 % CPU that could steal cycles during long runs.
  - Disk latency remains negligible (iostat shows ≈0.2 ms waits, <1 % util), confirming WAL fsync latency—not hardware bandwidth—is limiting response time.

  Next Steps

  - Keep amplifying group commit by batching API writes or setting synchronous_commit='local'/'off' on idempotent paths to shrink the 176 s fsync bill.
  - Allow the WAL writer to flush more aggressively (e.g., wal_writer_delay = 10ms) and review checkpoint spacing to avoid bursts overlapping with peak load.
  - Schedule a short job to VACUUM (ANALYZE) or TRUNCATE dms.ReferenceStage between load runs so probe statistics stay accurate.
  - If the backup process isn’t required during tests, suspend it to leave more CPU headroom for Postgres and the DMS service.

### Asked about improvement from group commit

• Group-Commit Impact

  - Client WAL writes dropped from 1 151 647 to 432 126 (‑62 %, pg_stat_io), and total client WAL write time fell from 20.7 s to 10.2 s (‑51 %).
  - Client WAL fsync time shrank from 450.9 s to 176.5 s (‑61 %), so each commit now waits ≈0.28 ms for durability instead of ≈0.39 ms (‑29 %).
  - WAL writes per commit fell from 1.01 to 0.68 (‑32 %), showing group commit is merging flush requests effectively.
  - COMMIT execution remained tiny (mean ≈0.0007 ms) and dms.InsertReferences mean latency stayed flat at ~1.66 ms with ~1.76 KB WAL per call, so the throughput gain comes from fewer/
    smaller fsyncs rather than faster per-call logic.

  Still Watching

  - A Borg backup (/usr/bin/borg check, pid 473721) is consuming ~88 % CPU; pause it during load tests to leave more headroom.
  - WAL fsync waits persist (one active WalSync session) so further batching or lowering wal_writer_delay could squeeze out more improvement.

### postgresql.conf tuning review

• The new group-commit settings helped, but the stats show we still burn 176 s in WAL fsyncs across 432 k commits (≈0.41 ms each). With synchronous_commit fixed at on, here’s how I’d tune
  ~/Downloads/temp/2025-11-03-11-06-postgresql.conf for more batching and fewer backend-driven flushes:

  - Tighten WAL writer cadence – Drop wal_writer_delay from 5 ms to 2 ms (line 254) and shrink wal_writer_flush_after from 1 MB to 256 kB (line 255). That keeps the background writer
    flushing behind the workload so foreground commits can piggyback instead of doing their own WalSync.
  - Broaden the commit hold window – Bump commit_delay to 1000 µs and lower commit_siblings to 3 (258‑259). The current 500 µs / 5 sibling gate is still letting many commits flush solo;
    doubling the window and lowering the threshold will catch more concurrent backends without adding noticeable latency.
  - Keep autovacuum ahead of deletes – With autovacuum_vacuum_cost_delay = 5ms and autovacuum_vacuum_cost_limit = 1000 (706‑709), workers still accumulate tens of thousands of dead tuples
    per reference partition. Consider cutting the delay to 1 ms and lifting the limit to 3000 so vacuum finishes faster, keeping visibility map bits hot and trimming full-page writes.
  - Stage table maintenance – dms.ReferenceStage is still cycling ~20 M rows per hour with 79 k dead tuples. Schedule a VACUUM (ANALYZE) or TRUNCATE between runs (outside postgresql.conf)
    so the equality probe stats stay accurate and your autovac workers stay focused on the partition tables.

  Those changes should shave the remaining WAL-sync wait while honoring the synchronous durability requirement.

### Test results - 1ms more latency, no throughput change

  Results Summary:
  - Duration: 31+ minutes (11:23 - 11:54)
  - Total Requests: 2,150,923
  - Failures: 1,480 (0.069% failure rate)
  - Throughput: 1,195 requests/second
  - Median Response Time: 8ms
  - 95th Percentile: 12ms
  - 99th Percentile: 23ms
  - Output: 34MB of detailed history data

  Comparison to Previous Run (2025-11-02-21-20):
  - Previous: 2,167,991 requests
  - Current: 2,150,923 requests ✓ (similar magnitude)
  - Previous: 1,204 req/s
  - Current: 1,195 req/s ✓ (comparable)
  - Previous: 7ms median
  - Current: 8ms median ✓ (very similar performance)


## Update - 2025-11-03-12-05-expand-group-commit (Doubled commit wait to 1ms, wal writer change above, no autovac change)

### This was worse

• PostgreSQL

  - Workload remains WAL-bound. Since the latest reset (pg_stat_wal 12:04:10), client backends issued 415 k WAL writes that took 12.8 s of write_time and 152 s of fsync time (pg_stat_io).
    WAL writer absorbed more work (70 k writes, 1.8 s write_time, 26 s fsync), but active sessions still show COMMIT waits for WalSync.
  - dms.InsertReferences is still the dominant SQL path: 492 k calls at 1.73 ms mean, 868 MB WAL (≈1.77 KB per call) and 86 M buffer hits (pg_stat_statements queryid -7737659587446346593).
    The paired INSERT INTO dms.Reference adds ~1.85 KB WAL per call, so each logical reference operation still emits ≈3.6 KB.
  - Function stats confirm 5.64 M invocations of InsertReferences consuming 9 223 s cumulative execution time (pg_stat_user_functions). Autovacuum remains active (currently on
    dms.document_01), keeping partition dead tuples manageable.
  - Compared to the previous run (post-group-commit tuning: 432 k writes, 10.2 s write_time, 176 s fsync), expanding the window didn’t materially lower flush counts (‑4 %) and increased
    write_time (+25 %) while trimming fsync time (‑14 %). Group commit is still the limiting factor; the change mostly shifted work to the WAL writer without reducing per-call WAL volume.

  System & Application

  - The DMS frontend (pid 443309) holds ~1 GB RSS and ~210 % CPU; logs show only routine restarts (no new errors).
  - The python load generator (pid 500865) uses ~73 % CPU with minimal memory, so it’s not throttling the test. No other heavy side processes are visible.
  - Host resources are healthy: CPUs average ~53 % idle (top), and NVMe latency remains ~0.2 ms with <3 % utilization (iostat). Swap is nearly full (≈0 MB free), so keep an eye on
    background services to avoid paging under heavier loads.

  Recommendations

  1. Further reduce commit flush frequency: batch DB operations per request or use synchronous_commit='local'/'off' for idempotent paths to shorten the 152 s fsync bill.
  2. Tune WAL writer/flush cadence (e.g., wal_writer_delay = 10ms) so the writer absorbs more group commits before clients reach WalSync.
  3. Keep the reference staging table tidy—schedule VACUUM (ANALYZE) or TRUNCATE between runs to prevent the equality probe stats from drifting.
  4. Monitor swap usage; freeing nonessential services (e.g., IDE, background jobs) during load tests will maximize headroom for Postgres and the DMS service.


### Shared the tuning that was done:

Prompt: The difference between the previous run and this run is that commit_delay changed from 500 to 1000, commit_siblings changed from 5 to 3, wal_writer_delay changed from 5 ms to 2 ms, and
  wal_writer_flush_after changed from 1 MB to 256kB. synchronous_commit must stay on. What tuning suggestions do you have, or have we reached the limits of tuning postgresql.conf?


• - The latest config change (commit_delay = 1000 µs, commit_siblings = 3, wal_writer_delay = 2 ms, wal_writer_flush_after = 256 kB) barely reduced commit flushes (down only 4 %) and
    actually lengthened client write time to 12.8 s (+25 %) while fsync time fell just 14 %. InsertReferences still emits ~1.77 KB WAL per call and commits once per request, so the tuning
    window is largely exhausted on the PostgreSQL side.
  - With synchronous_commit locked at on, two knobs still worth testing:
      - Raise the aggregation window rather than shrink it: try wal_writer_delay = 10ms (even 20 ms) and bump wal_writer_flush_after back to ≥1 MB so the background writer absorbs more log
        without forcing client fsyncs.
      - Keep commit_delay conservative (500–2000 µs) but set commit_siblings higher (8–16) so the delay only activates when several sessions queue together; the current value of 3 fires the
        delay even in light contention and costs latency without gaining much.
      - Monitor pg_stat_io for the resulting write/fsync deltas after each change.
  - Beyond that, more configuration tweaks won’t deliver material gains. To shrink the 152 s fsync bill you’ll need to change workload shape:
      1. Batch API work so each transaction commits multiple reference operations.
      2. Identify idempotent paths where SET LOCAL synchronous_commit = 'local' or 'off' is acceptable.
      3. Ensure the WAL device has headroom (dedicated NVMe, low-latency mount options) because every flush now costs ~0.36 ms.

  If you can’t restructure commits or relax durability, PostgreSQL’s config is already near its useful limit; future wins will come from the application layer or faster WAL hardware rather
  than more postgresql.conf tuning.


## Update - 2025-11-03-14-51-rerun-of-11-06-group-commit-tuning-after-vac  (Rerun of 2025-11-03-11-06-group-commit-tuning was slower)

• - InsertReferences is still the hottest query: 472 998 calls at 1.65 ms average with 834 MB total WAL (≈1.76 KB/call), and the paired INSERT INTO dms.Reference contributes another
    ≈1.85 KB/call (pg_stat_statements queryids -7737659587446346593 and 6070861028664210120).
  - WAL durability remains the bottleneck: since the 15:33 reset, client backends have issued 612 447 WAL writes for 14.5 s write time and 212.6 s fsync time (pg_stat_io), and active
    sessions show WalSync waits on commits ( pg_stat_activity).
  - Autovacuum is keeping up but busy: it’s currently vacuuming dms.document_01, and the stage table has handled 33.9 M insert/delete cycles with 78 k dead rows, last vacuumed at 15:45
    (pg_stat_all_tables).
  - No application faults observed; the frontend process just restarted at 14:49 and is running normally (src/dms/frontend/EdFi.DataManagementService.Frontend.AspNetCore/
    logs/20251103.log:1). Idle-in-transaction sessions still hold FOR NO KEY UPDATE locks, so tighten connection handling to avoid extra autovac pressure.
  - The python load generator (pid 582222) runs at ~73 % CPU with 64 MB RSS, so it isn’t CPU-bound or throttling the test; however, an unrelated Borg backup (/usr/bin/borg check,
    pid 597523) is consuming ~99 % CPU and Chrome is using ~81 %, which compete for cores and could inflate response times (top).
  - Storage is healthy—iostat shows ≈0.2 ms waits and <1 % utilization—so latency is driven by commit fsyncs rather than raw IO bandwidth. Swap remains saturated (≈8 GB in use), so consider
    freeing memory to prevent future contention.

  Next steps

  1. Pause the backup/Chrome workloads during load testing so Postgres and the DMS service have more CPU headroom.
  2. Continue encouraging group commit (batch app transactions or use synchronous_commit='local'/'off' for idempotent paths) to reduce the 212 s fsync cost.
  3. Keep vacuuming dms.ReferenceStage between runs and close idle-in-transaction sessions promptly to limit lock hold times and autovac churn.

### Direct comparison ask

• Comparison vs prior run

  - Query timing: dms.InsertReferences stays essentially flat (1.65 ms now vs 1.66 ms before) and still emits ~1.76 KB WAL per call. The companion INSERT INTO dms.Reference behaves
    similarly (~0.52 ms, ~1.85 KB WAL). So core SQL latency is unchanged.
  - WAL workload: Client WAL writes rose from 432 k to 612 k (+42 %), and total client fsync time climbed from 176 s to 213 s (+21 %). That’s the main regression; fewer commits are getting
    grouped before flush.
  - System noise: This run had extra CPU consumers (e.g., borg check at ~99 % CPU, Chrome at ~81 %), so Postgres and the DMS service had less headroom. Disk latency and app behavior remain
    healthy.

  Overall, query performance matches the previous run, but more scattered commits and competing CPU workloads increased WAL flush volume and fsync time, so throughput isn’t quite as good.
  Pausing the background jobs and tightening transaction batching should bring it back in line.


### Transaction tightening ask

• To boost batching you need to reduce the number of independent commits the application issues during a burst. A few practical levers:

  - Wrap related work in a single unit-of-work. If a request currently does INSERT Document, InsertReferences, and cleanup each in its own transaction, wrap them in one transaction scope so they share
    a single COMMIT.
  - Buffer writes before committing. In bulk loaders or background jobs, gather N operations (e.g., 50–100 resource mutations) and execute them inside one transaction instead of committing after every
    record.
  - Reuse open commands within an existing transaction. Ensure the .NET code doesn’t open a fresh connection/transaction for each reference; use a shared connection/transaction per request and avoid
    “idle in transaction” gaps.
  - Tune client batching knobs. If you’re using Dapper/ADO, disable automatic auto-commit and explicitly call BeginTransaction/Commit. For EF Core, use SaveChanges() less frequently (e.g., after
    processing a batch).
  - Control API callers. If upstream services fire many single-row mutations, expose batch endpoints so they can post multiple changes per call, allowing the service to wrap them together.
  - Add commit throttling logic. For high-volume background tasks, queue mutations and flush at a fixed interval or when a buffer threshold is reached, keeping commit frequency steady and group-commit
    friendly.
  - Watch connection pooling. Ensure pooling keeps sessions alive so transaction batching is effective; churn that reopens sessions for each call often forces extra commits.

  Implementing even one or two of these changes should lower commit frequency enough for the group-commit settings to bite harder without altering PostgreSQL again.

### Results

  Overall Performance (Aggregated)

  | Metric                | Value                       |
  |-----------------------|-----------------------------|
  | Total Requests        | 2,155,424                   |
  | Failures              | 1,638 (0.076% failure rate) |
  | Median Response Time  | 8ms                         |
  | Average Response Time | 7.44ms                      |
  | Min Response Time     | 1ms                         |
  | Max Response Time     | 316ms                       |
  | Throughput            | 1,197.47 req/s              |
  | 95th Percentile       | 12ms                        |
  | 99th Percentile       | 14ms                        |
  | 99.9th Percentile     | 22ms                        |




Here's a question:

How do we monitor

1. No references changed ** done
2. It's all new (insert) ** done
3. It's an update and
  1. We should use on conflict
  2. We should use merge

How about a heuristic that we check if the counts are the same. If so, it's likely a small change or none at all.

Should we instrument this and see if we can tune further that way?

- Tweak checkpoint cadence
- Aggressive AUTOVACUUM of staging table
- compression options?
