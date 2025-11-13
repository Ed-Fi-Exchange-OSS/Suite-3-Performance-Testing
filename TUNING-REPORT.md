After work to resolve PostgreSQL WAL write flushing issues at lower transaction volumes and a fix to an obvious DMS latency issue with continuous JSON Schema recompiles, on my high-end laptop DMS handles a sustained (1 hour) throughput of 3,200 requests/sec with 7.6ms average latency. Database writes at this load are 16 MB/sec and DB-only latency averages 3.6ms.

Though the system is heavily loaded, the throughput number is limited at that rate by the Suite 3 Performance Test running on the same laptop, not by either DMS or PostgreSQL. Pushing it higher would cause contention with DMS itself.

Opportunities to further reduce DMS latency (removing unnecessary JSON serial/deserializations) look promising but have not be investigated.

This DMS configuration has both authorization and streaming disabled.



Possible next steps:

- Further tuning
    - Profile DMS for latency reduction opportunities
- Further metrics
    - Get comparative data with replication on
    - Move load tester to separate system and test with additional load




