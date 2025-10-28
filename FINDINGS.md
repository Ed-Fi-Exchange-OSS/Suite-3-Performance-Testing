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
