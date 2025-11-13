Current Load

  - 20-client edfi_performance_test run (PID 132649) has been executing ~17 min; pidstat shows it steady at 82–88 % user CPU on a single core with 0 % wait and trivial memory, so the
    harness is healthy but inherently single-process—it is not saturating the 24-core host.
  - Host telemetry remains light: load averages 8.85/8.98/7.23 with vmstat 1 still showing 59–61 % idle CPU and <2 % iowait, free -h leaves 48 GiB RAM available, and iostat -xz reports
    NVMe1n1 utilization ≤32 % with 0.14 ms await. No systemic CPU, memory, or storage pressure was introduced by the extra clients.

  Database Health

  - pg_stat_activity lists only six non-idle sessions and the wait summary is dominated by ClientRead; PostgreSQL is typically waiting for the ASP.NET Core service rather than for locks or
    I/O.
  - pg_stat_statements (reset 16:41:56) shows the same reference ingestion chain as the top consumer:
    • dms.InsertReferences → 618,906 calls (≈610/s) at 1.73 ms mean, 1.03 GB WAL.
    • INSERT INTO dms.Reference…ON CONFLICT → 586,644 calls at 0.54 ms mean, 1.03 GB WAL.
    • DELETE FROM dms.Document… → 429,396 calls at 0.75 ms mean, 0.13 GB WAL.
    Execution times remain sub‑2 ms, so PostgreSQL is not the latency bottleneck even with ~2 MB/s WAL generation (pg_stat_wal: 2.36 GB since 16:41:44, no buffer-full events).
  - pg_stat_io attributes just 2,449 shared-block reads (≈19 MB, 0.10 s read time) vs 890,126 writes (≈9 GB, 15.6 s write time) for client backends in this interval, matching the healthy
    NVMe metrics and confirming the workload is WAL/CPU heavy, not read heavy.
  - Autovacuum churn persists: dms.ReferenceStage holds ~163 k dead tuples with 74 autovac runs since the stats reset, and multiple reference_% partitions each have ~50 k dead rows
    even though their latest autovac finished seconds earlier. The shared unlogged staging table plus row-by-row deletes remain the main source of background work, but they have not yet
    manifested as blocking waits.

  Application & Response-Time Bottlenecks

  - The DMS ASP.NET Core process (PID 87917) now burns ~245 % CPU (≈2.5 cores) continuously, whereas PostgreSQL as a whole uses only ~6 cores (pidstat -C postgres). With >12 cores still
    idle, end-to-end response time is application-bound, not database-bound.
  - Despite doubling client count, only ~6 database sessions are active at any moment—suggesting the C# service thread pool or Npgsql connection pool is limiting concurrency. ClientRead
    waits on the database confirm the backend frequently waits for the app to consume results.
  - There are still no WALWrite/WalSync waits, lock contention, or disk-latency spikes; synchronous_commit=on remains acceptable because flush latency stays sub-millisecond on NVMe.

  Load-Test Driver Check

  - The Python harness consumes <1 core and exhibits no iowait or memory pressure, so it is not distorting the test. To truly realize 20+ concurrent clients, you may need multiple driver
    processes or to run the generator from another host; the current single process can only push what one CPU core can schedule.

  Overall, even with 20 clients, PostgreSQL 18 remains comfortably within CPU, memory, and I/O limits; the dominant bottleneck for response time is still the DMS C# application layer rather
  than the database or the load harness.
