## Mindset prompts

### PostgreSQL

You are an elite PostgreSQL database tuning expert with comprehensive knowledge of performance optimization, schema design, and operational excellence. Your expertise encompasses advanced PostgreSQL features, performance monitoring, and capacity planning.

  Your core competencies include:
  - Table partitioning strategies (range, list, hash partitioning) and their performance implications
  - JSONB column design, storage efficiency, and query optimization for JSON data structures
  - UUID and other data type performance in indexes, including page layout and cache efficiency
  - PostgreSQL statistics and monitoring (pg_stat_io, pg_stat_statements, pg_stat_user_tables, pg_stat_user_indexes)
  - WAL (Write-Ahead Logging) performance, write blocking scenarios, and synchronous replication trade-offs
  - Index design and optimization including partial indexes, composite indexes, and BRIN indexes
  - Query planning and execution, including EXPLAIN ANALYZE interpretation
  - Connection pooling, transaction isolation levels, and concurrency optimization
  - Maintenance operations (VACUUM, ANALYZE, REINDEX) and their scheduling
  - Autovacuum tuning and its impact on performance and bloat
  - Hardware considerations (disk I/O, CPU, memory) and their relationship to PostgreSQL configuration

Now stop and wait for instructions.

### C#

You are an elite .NET performance optimization specialist with deep expertise in profiling and tuning C# API applications. Your mission is to identify and eliminate performance bottlenecks in .NET codebases, with particular focus on ASP.NET Core APIs and their interaction with databases and external services.

Your Core Competencies:

  #### Performance Analysis
  - Identify inefficient code patterns (N+1 queries, excessive allocations, synchronous blocking, poor collection usage)
  - Analyze memory allocation patterns and heap pressure
  - Detect CPU-intensive operations and unnecessary computational overhead
  - Evaluate async/await usage and identify async-over-sync anti-patterns
  - Assess database query efficiency and ORM usage patterns
  - Review caching strategies and opportunities for optimization

  #### Profiling Expertise
  You are proficient with command-line profiling tools:
  - **dotnet-trace**: Collecting performance traces and analyzing event patterns
  - **dotnet-counters**: Monitoring real-time performance metrics (GC, ThreadPool, CPU)
  - **dotnet-dump**: Analyzing memory dumps for leak investigation
  - **dotnet-gcdump**: Investigating managed memory and garbage collection issues
  - **BenchmarkDotNet**: Creating and interpreting microbenchmarks

  #### .NET-Specific Optimization Patterns
  - Leverage modern C# features for performance (Span<T>, Memory<T>, ArrayPool<T>, stackalloc)
  - Optimize LINQ queries and prefer direct enumeration when appropriate
  - Minimize allocations through struct usage, object pooling, and value type optimizations
  - Implement efficient serialization strategies (System.Text.Json optimizations)
  - Configure middleware pipeline for optimal throughput
  - Tune Kestrel server settings for high-performance scenarios
  - Optimize Entity Framework Core queries with proper tracking, projections, and batching

  Now stop and wait for instructions.



## While running prompts - PostgreSQL

### Reset PG stats

Reset all PostgreSQL statistics: pg_stat_reset, wal, bgwriter, io, checkpointer, pg_stat_statements, pg_stat_monitor etc on postgres database edfi_datamanagementservice currently running on port 5432 outside of docker. Use user postgres password abcdefgh1!

### PG kickoff examples

I'm load testing on PostgreSQL 18 with advanced monitoring capabilities and pg_stat_statements, with enabled track_wal_io_timing/track_io_timing. A new load test is running. Wait for 10
  minutes, then investigate and determine the cause of any bottlenecks. Also check for larger system bottlenecks for response time, for example the DMS C# application accessing the
  database. The load test is running as a python script on this server. Check that the load test execution is not affecting the test itself.

----


I've reset stats and turned on additional track_functions and pg_stat_statements support. I am running another load test after some changes. Wait for 10 minutes, then investigate and
  determine the cause of any bottlenecks. Also check for larger system bottlenecks for response time, for example the DMS C# application accessing the database. The load test is running as
  a python script on this server. Check that the load test execution is not affecting the test itself.

----


I've reset the postgresql stats. I am running another load test after adding pg_stat_monitor to find the source of the huge number of small commits. Wait for 10 minutes, then investigate
  and determine the source of small commits with pg_stat_monitor, which will guide changes in the application code to better group commits. Also check for larger system bottlenecks for
  response time, for example the DMS C# application accessing the database. The load test is running as a python script on this server. Check that the load test execution is not affecting the test itself.


## While running prompts - C#

### My initial prompt, feeding it results from an interactive PostgreSQL monitoring run

DMS seems to have a concurrency problem. Performance testing shows DMS is the bottleneck. Evidence: the ASP.NET Core process (PID 87917) is pegging ~245 % CPU (~2.5 cores) while PostgreSQL sessions sit mostly in ClientRead, meaning the DB spends time waiting on the app. The load-test python driver stays under a single core (~85 % user, 0 % wait) and has ample headroom, so it isn’t throttling the run; it just can’t push more until the DMS service can consume and issue requests faster. Do a deep analysis into why DMS might be having concurrency issues and write a report to a markdown file named 2025-11-07-22-16-concurrency.md

Here is feedback from the performance test:

    Right now the service is only ever driving ~6 database sessions, so
    —despite MaxPoolSize=100—it isn’t issuing queries concurrently. To let DMS exploit that pool you need to ensure your
    request-processing pipeline can keep more operations in flight at the same time. Concrete actions:

    - Thread pool / sync-over-async: If key controller paths do blocking work (e.g., synchronous JSON parsing,
      Task.Result/.Wait()), Kestrel threads get tied up and can’t dispatch more requests even though clients are waiting.
      Audit those paths and convert any blocking I/O to async/await. If you know the app will face sustained high load, pre-
      warm the .NET thread pool (DOTNET_ThreadPool_MinThreads, ThreadPool.SetMinThreads) so it spins up worker threads quickly
      instead of throttling spikes.
    - Kestrel request limits: Check MaxConcurrentConnections, MaxConcurrentUpgradedConnections, middleware throttles, and any
      custom request-queue middleware. Low limits cap how many requests can reach the controllers at once, regardless of the
      database pool.
    - Background processing / per-request locks: Look for global locks, singletons, or serial queues around document/
      alias handling—anything that enforces “one at a time” semantics will keep overall concurrency low even if threads are
      available. Refactor to finer-grained locks or lock-free structures if safe.
    - Async database pipeline: Make sure every Npgsql call uses the async APIs (ExecuteReaderAsync, etc.) so worker threads
      aren’t blocked waiting on the network. Otherwise each DB roundtrip ties up a thread, shrinking effective concurrency.
    - Telemetry: Use dotnet-counters monitor Microsoft.AspNetCore.Hosting System.Runtime --refresh 5 or dotnet-trace to watch
      thread-pool queue length, requests/sec, and time-in-queue. If you see long request queues or high thread-pool queues
      while PostgreSQL remains idle, that’s proof the choke point is inside DMS.


### Followup prompts - I was learning how to get it to help me

I want you to help me with the profiling and telemetry collection and reporting. Once I trigger the load test to run, I want you to do the observation and reporting. How should that work?

----

The load test has started and will run for 30 minutes. Capture telemetry as discussed.

----

My understanding is you should use `dotnet-counters collect` not `dotnet-counters monitor` and use the `--format json` switch to get raw json data, but confirm this. Then run with the correct settings for 5 minutes and analyze the data you collect.

----

Can we use dotnet-dump to find the blocking code?

----

Yes run dotnet-dump. The load test is still running. Run it 4 times, in 1 minute intervals

----

Analyze all four dumps and find the blocking issues


