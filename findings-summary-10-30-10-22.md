## Baseline findings - no References table, no auth processing
- Load tests pinned commit latency on `WALSync/WALWrite`; nearly every single-statement transaction forced its own fsync, Debezium `REPLICA IDENTITY FULL` inflated row images, and dead tuples piled up on document/alias partitions despite autovacuum keeping pace.

## 2025-10-26 Drop auth JSONBs and Document replication
- Removing logical replication artifacts and dropping the authorization JSONB column cleared sustained WAL waits (nvme flush ≈0.13 ms) and shrank dead tuples from ~50 k to ~5 k per partition, shifting the bottleneck from storage to commit rate management.

## 2025-10-26 16:41 Add missing index, tuning
- Adding the alias FK index plus config tuning cut cascade deletes from 215 ms full scans to 0.38 ms indexed probes, while 2.8 k commits/s at ~0.33 ms per flush confirmed the WAL path had headroom and that application CPU now dominated host load.

## 2025-10-26 17:28 Bring back replication
- Re-enabling `wal_level=logical` added 10–12 % WAL overhead yet kept flush latency ~0.19 ms and autovacuum healthy, proving the platform can sustain logical decoding once archives are sized for the higher byte rate.

## 2025-10-27 18:46 UUIDv7, Npgsql tuning, additional monitoring
- Sequential DocumentUuid generation and new WAL timers showed group commit efficiency (~0.55 flushes per commit, 55 MB/30 s) with dead tuples capped at 1–7 k, leaving DMS-side CPU as the emerging ceiling.

## 2025-10-27 22:15 PostgreSQL 18 for even more monitoring
- The PG 18 upgrade maintained sub-ms query and WAL performance (473 MB/30 s at 0.33 ms/flush) but exposed operational asks—tame 2 GB autovacuum workers, clean up DISCARD ALL storms, and enforce prompt closeout of `SELECT FOR UPDATE` sessions.

## 2025-10-28
- No notes, but got to point comfortable to bring back References table

## 2025-10-29 15:57 Bring back References table with modified schemas
- Loading the reference dataset drove sustained 17 MB/s WAL and surfaced 101 ms joins from partition-mismatch scans, while aggressive `work_mem`/`maintenance_work_mem` let autovacuum lag on the new partitions.

## Current focus: Fix References - Alias queries
- Refine the reference schema to remove partition-mismatch scans, right-size memory knobs, and keep per-run pg_stat_wal/io/statements snapshots to hold the WAL path steady as load grows.
