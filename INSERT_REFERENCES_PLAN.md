• I'm preparing two SQL prototype designs: a differential update using set operations and a partition-local staging approach with temp tables. I'll also suggest improvements for how the
  call side handles arrays and return values, aiming to streamline network usage and better handle invalid references, while emphasizing concurrency and locking considerations. The final
  message will include detailed code snippets and structured sections covering these ideas.

─ Worked for 12s ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

• Differential-Update Prototype

  -- SPDX…
  CREATE OR REPLACE FUNCTION dms.InsertReferences_Diff(
      parent_document_id bigint,
      parent_document_partition_key smallint,
      referential_ids uuid[],
      referential_partition_keys smallint[]
  ) RETURNS boolean
  LANGUAGE plpgsql
  AS $$
  DECLARE
      invalid_ids uuid[];
  BEGIN
      WITH input_rows AS (
          SELECT
              parent_document_id      AS parentdocumentid,
              parent_document_partition_key AS parentdocumentpartitionkey,
              unnest_ids.referentialid,
              unnest_ids.referentialpartitionkey,
              a.id                    AS aliasid,
              a.documentid            AS aliasdocumentid,
              a.documentpartitionkey  AS aliasdocumentpartitionkey
          FROM unnest(
                  referential_ids,
                  referential_partition_keys
               ) AS unnest_ids(referentialid, referentialpartitionkey)
          LEFT JOIN dms.alias a
                ON a.referentialid = unnest_ids.referentialid
               AND a.referentialpartitionkey = unnest_ids.referentialpartitionkey
      ),
      updatable AS (
          SELECT i.*, r.aliasid AS existing_aliasid,
                 r.referenceddocumentid,
                 r.referenceddocumentpartitionkey
          FROM input_rows i
          LEFT JOIN dms.reference r
                 ON r.parentdocumentid = i.parentdocumentid
                AND r.parentdocumentpartitionkey = i.parentdocumentpartitionkey
                AND r.referentialpartitionkey = i.referentialpartitionkey
                AND r.aliasid = i.aliasid
      ),
      deleted AS (
          DELETE FROM dms.reference r
          WHERE r.parentdocumentid = parent_document_id
            AND r.parentdocumentpartitionkey = parent_document_partition_key
            AND NOT EXISTS (
                SELECT 1
                FROM input_rows i
                WHERE i.referentialpartitionkey = r.referentialpartitionkey
                  AND i.aliasid = r.aliasid
            )
          RETURNING 1
      ),
      inserted AS (
          INSERT INTO dms.reference (
              parentdocumentid,
              parentdocumentpartitionkey,
              aliasid,
              referentialpartitionkey,
              referenceddocumentid,
              referenceddocumentpartitionkey
          )
          SELECT
              parentdocumentid,
              parentdocumentpartitionkey,
              aliasid,
              referentialpartitionkey,
              aliasdocumentid,
              aliasdocumentpartitionkey
          FROM updatable
          WHERE aliasid IS NOT NULL
            AND existing_aliasid IS NULL
          RETURNING 1
      ),
      updated AS (
          UPDATE dms.reference r
             SET referenceddocumentid = u.aliasdocumentid,
                 referenceddocumentpartitionkey = u.aliasdocumentpartitionkey
          FROM updatable u
          WHERE r.parentdocumentid = u.parentdocumentid
            AND r.parentdocumentpartitionkey = u.parentdocumentpartitionkey
            AND r.aliasid = u.aliasid
            AND r.referentialpartitionkey = u.referentialpartitionkey
            AND (
                r.referenceddocumentid <> u.aliasdocumentid
             OR r.referenceddocumentpartitionkey <> u.aliasdocumentpartitionkey
            )
          RETURNING 1
      )
      SELECT coalesce(array_agg(referentialid), '{}')
      INTO invalid_ids
      FROM input_rows
      WHERE aliasid IS NULL;

      RETURN invalid_ids = '{}';
  END;
  $$;

  - Accepts a single parent document instead of repeating it in arrays, so execution stays in one partitioned leaf.
  - Deletes only rows that don’t appear in the incoming payload.
  - Inserts only new alias links and updates rows when the alias’s document targets change.
  - Returns true when all references resolved, allowing the caller to skip materializing a result set in the common case. (See “Return-path options” below.)

  Partition-Local Staging Prototype

  CREATE OR REPLACE FUNCTION dms.InsertReferences_WithStage(
      parent_document_id bigint,
      parent_document_partition_key smallint,
      referential_ids uuid[],
      referential_partition_keys smallint[]
  ) RETURNS TABLE(invalid_referential_id uuid)
  LANGUAGE plpgsql
  AS $$
  BEGIN
      CREATE TEMP TABLE IF NOT EXISTS dms.temp_reference_stage
      (
          parentdocumentid               bigint,
          parentdocumentpartitionkey     smallint,
          referentialpartitionkey        smallint,
          referentialid                  uuid,
          aliasid                        bigint,
          referenceddocumentid           bigint,
          referenceddocumentpartitionkey smallint
      ) ON COMMIT DROP;

      TRUNCATE dms.temp_reference_stage;

      INSERT INTO dms.temp_reference_stage (
          parentdocumentid,
          parentdocumentpartitionkey,
          referentialpartitionkey,
          referentialid,
          aliasid,
          referenceddocumentid,
          referenceddocumentpartitionkey
      )
      SELECT
          parent_document_id,
          parent_document_partition_key,
          ids.referentialpartitionkey,
          ids.referentialid,
          a.id,
          a.documentid,
          a.documentpartitionkey
      FROM unnest(
              referential_ids,
              referential_partition_keys
           ) AS ids(referentialid, referentialpartitionkey)
      LEFT JOIN dms.alias a
             ON a.referentialid = ids.referentialid
            AND a.referentialpartitionkey = ids.referentialpartitionkey;

      -- Operate on the single target partition using the staged rows.
      DELETE FROM dms.reference p
      WHERE p.parentdocumentid = parent_document_id
        AND p.parentdocumentpartitionkey = parent_document_partition_key
        AND NOT EXISTS (
              SELECT 1
              FROM dms.temp_reference_stage s
              WHERE s.aliasid = p.aliasid
                AND s.referentialpartitionkey = p.referentialpartitionkey
        );

      INSERT INTO dms.reference (
          parentdocumentid,
          parentdocumentpartitionkey,
          aliasid,
          referentialpartitionkey,
          referenceddocumentid,
          referenceddocumentpartitionkey
      )
      SELECT
          parentdocumentid,
          parentdocumentpartitionkey,
          aliasid,
          referentialpartitionkey,
          referenceddocumentid,
          referenceddocumentpartitionkey
      FROM dms.temp_reference_stage
      WHERE aliasid IS NOT NULL
        AND NOT EXISTS (
              SELECT 1
              FROM dms.reference p
              WHERE p.parentdocumentpartitionkey = parent_document_partition_key
                AND p.parentdocumentid = parent_document_id
                AND p.aliasid = dms.temp_reference_stage.aliasid
                AND p.referentialpartitionkey = dms.temp_reference_stage.referentialpartitionkey
        );

      RETURN QUERY
      SELECT referentialid
      FROM dms.temp_reference_stage
      WHERE aliasid IS NULL;
  END;
  $$;

  - Uses a per-session temp table (≈17 KB for 30 references), keeping planner/executor focused on the target partition and minimizing repeated unnest work.
  - Lets you add indexes to the temp table (CREATE INDEX ON temp_reference_stage(referentialpartitionkey, aliasid);) if you need to speed up anti-joins or duplicates detection.
  - By reusing the temp table in the session you also enable future COPY-based loaders or batching multiple parents per transaction.

  Caller Optimizations (SqlAction.InsertReferences)

  1. Scalar Parent Parameters
     Update both prototypes to accept scalar parent document id/partition key; change the C# invocation to pass scalars instead of length-N arrays. That removes two array allocations per
     call and reduces parameter payload size. Example:

     await using var command = new NpgsqlCommand(
         "SELECT dms.InsertReferences_Diff($1, $2, $3, $4)",
         connection,
         transaction)
     {
         Parameters =
         {
             new() { Value = bulkReferences.ParentDocumentId },
             new() { Value = bulkReferences.ParentDocumentPartitionKey },
             new() { Value = bulkReferences.ReferentialIds },
             new() { Value = bulkReferences.ReferentialPartitionKeys },
         },
     };
  2. Binary Import (Optional)
     When batch sizes spike (e.g., 50+ references), consider writing to a temp table via COPY using NpgsqlBinaryImporter within the same transaction, then calling the staging function with
     just the parent key. This removes array parameter marshalling overhead and leverages sequential writes.
  3. Reuse Prepared Statements
     If the same SQL text is executed repeatedly, call command.Prepare() once per connection to pin the plan. Combined with scalar parent parameters, the executor can stay in a single
     partition with stable plan shapes.
  4. Avoid Materializing Reader When Not Needed
     If the function returns boolean, the caller can simply read a scalar via ExecuteScalarAsync instead of streaming a result set. If you keep the table-returning signature, wrap the read
     in an early exit (e.g., if (!reader.HasRows) return Array.Empty<Guid>();).

  Return-Path Options for Invalid IDs

  Since <0.2 % of calls currently yield invalid referential IDs, you can trim the hot-path cost by moving the detailed list behind a separate call:

  1. Boolean Return + Audit Table
      - Function returns false when any alias lookup fails.
      - When failures happen, insert the offending IDs into a session-specific temp table or a short-lived permanent table keyed by (trace_id, parent_document_id, transaction_timestamp).
      - Caller receives false and decides whether to abort (likely) or fetch details via a lightweight SELECT * FROM dms.ReferenceInvalidLog WHERE trace_id = $1.
  2. Exception on Failure
      - If invalid referential IDs should abort the transaction, RAISE EXCEPTION USING DETAIL = array_to_string(...) eliminates result-set handling entirely.
      - Caller can catch the PostgreSQL error code (custom SQLSTATE 'P0001') and extract the detail message to surface in API errors.
  3. Two-Step API
      - Provide dms.TryInsertReferences returning a boolean and storing invalid IDs in a temp table.
      - Expose dms.FetchInvalidReferences(parent_document_id, parent_partition_key) for the rare debugging path.

  All options remove the ProjectSet overhead from the common path and let the C# side use simple ExecuteScalarAsync<bool> calls.

  Next Steps

  1. Prototype both SQL functions in a scratch schema; gather pg_stat_statements deltas (calls, shared_blks_hit, wal_bytes) under the load harness to quantify savings.
  2. Adjust the C# caller to pass scalar parent keys and swap in the chosen function. Capture GC profiles to confirm array allocation drops.
  3. Decide on the new return contract; update service logic and integration tests accordingly.
  4. If differential update is effective, drop the old INSERT triggers/index maintenance logic, and revisit autovacuum thresholds per partition to reflect lower churn.

  Happy to help translate the winning prototype into production migration scripts when you’re ready.

--------------

Winner?

Why ON CONFLICT helps
  Once each (parentdocumentpartitionkey, parentdocumentid, aliasid) combination is unique, INSERT … ON CONFLICT … DO UPDATE lets us refresh rows without the extra update statement in the
  differential prototype. We still need a post-insert DELETE to remove references that disappeared from the payload, but inserts/updates collapse into one statement and reduce FK trigger
  work. Because dms.reference is list-partitioned, PostgreSQL requires the supporting unique index to exist on every leaf partition (global unique indexes aren’t available yet).

  ———

  1. Add a parent+alias unique index (online migration)

  -- run once during a maintenance window
  DO $$
  DECLARE
      partition regclass;
  BEGIN
      FOR partition IN
          SELECT inhrelid
          FROM pg_inherits
          WHERE inhparent = 'dms.reference'::regclass
      LOOP
          EXECUTE format(
              'CREATE UNIQUE INDEX CONCURRENTLY IF NOT EXISTS %I_parent_alias_uix
                 ON %s (parentdocumentpartitionkey, parentdocumentid, aliasid);',
              partition::text,
              partition
          );
      END LOOP;
  END;
  $$;

  -- define parent-level constraint so future partitions inherit the rule
  ALTER TABLE ONLY dms.reference
      ADD CONSTRAINT reference_parent_alias_unique
      UNIQUE USING INDEX reference_00_parent_alias_uix; -- pick any existing partition index

  (Choose the first partition’s index as the template; subsequent partitions inherit the constraint automatically.)

  ———

  2. ON CONFLICT function using the temp staging table

  CREATE OR REPLACE FUNCTION dms.InsertReferences_OnConflict(
      parent_document_id bigint,
      parent_document_partition_key smallint,
      referential_ids uuid[],
      referential_partition_keys smallint[]
  ) RETURNS boolean
  LANGUAGE plpgsql
  AS $$
  DECLARE
      invalid boolean;
  BEGIN
      CREATE TEMP TABLE IF NOT EXISTS dms.temp_reference_stage
      (
          parentdocumentid               bigint,
          parentdocumentpartitionkey     smallint,
          referentialpartitionkey        smallint,
          referentialid                  uuid,
          aliasid                        bigint,
          referenceddocumentid           bigint,
          referenceddocumentpartitionkey smallint
      ) ON COMMIT PRESERVE ROWS;

      TRUNCATE dms.temp_reference_stage;

      INSERT INTO dms.temp_reference_stage
      SELECT
          parent_document_id,
          parent_document_partition_key,
          ids.referentialpartitionkey,
          ids.referentialid,
          a.id,
          a.documentid,
          a.documentpartitionkey
      FROM unnest(referential_ids, referential_partition_keys)
              AS ids(referentialid, referentialpartitionkey)
      LEFT JOIN dms.alias a
             ON a.referentialid = ids.referentialid
            AND a.referentialpartitionkey = ids.referentialpartitionkey;

      WITH upsert AS (
          INSERT INTO dms.reference (
              parentdocumentid,
              parentdocumentpartitionkey,
              aliasid,
              referentialpartitionkey,
              referenceddocumentid,
              referenceddocumentpartitionkey
          )
          SELECT
              parentdocumentid,
              parentdocumentpartitionkey,
              aliasid,
              referentialpartitionkey,
              referenceddocumentid,
              referenceddocumentpartitionkey
          FROM dms.temp_reference_stage
          WHERE aliasid IS NOT NULL
          ON CONFLICT ON CONSTRAINT reference_parent_alias_unique
          DO UPDATE
             SET referenceddocumentid = EXCLUDED.referenceddocumentid,
                 referenceddocumentpartitionkey = EXCLUDED.referenceddocumentpartitionkey
             WHERE (dms.reference.referenceddocumentid,
                    dms.reference.referenceddocumentpartitionkey)
                 IS DISTINCT FROM
                   (EXCLUDED.referenceddocumentid,
                    EXCLUDED.referenceddocumentpartitionkey)
          RETURNING 1
      )
      DELETE FROM dms.reference r
      WHERE r.parentdocumentid = parent_document_id
        AND r.parentdocumentpartitionkey = parent_document_partition_key
        AND NOT EXISTS (
              SELECT 1
              FROM dms.temp_reference_stage s
              WHERE s.aliasid = r.aliasid
                AND s.referentialpartitionkey = r.referentialpartitionkey
        );

      invalid :=
          EXISTS (
              SELECT 1
              FROM dms.temp_reference_stage
              WHERE aliasid IS NULL
          );

      RETURN NOT invalid;
  END;
  $$;

  - Inserts and updates happen in a single statement; FK triggers run only once per reference.
  - The DELETE removes references no longer present in the payload.
  - The function returns true when every referential ID resolved; callers that need the exact failures can query the temp table (e.g., SELECT referentialid FROM dms.temp_reference_stage
    WHERE aliasid IS NULL;) or a dedicated logging table if cross-transaction visibility is required.

  ———

  3. C# caller changes (single parent, boolean result)
  src/dms/backend/EdFi.DataManagementService.Backend.Postgresql/Operation/SqlAction.cs:512

  await using var command = new NpgsqlCommand(
      "SELECT dms.InsertReferences_OnConflict($1, $2, $3, $4)",
      connection,
      transaction)
  {
      Parameters =
      {
          new() { Value = bulkReferences.ParentDocumentId },
          new() { Value = bulkReferences.ParentDocumentPartitionKey },
          new() { Value = bulkReferences.ReferentialIds },
          new() { Value = bulkReferences.ReferentialPartitionKeys }
      }
  };

  var success = (bool)await command.ExecuteScalarAsync();
  if (!success)
  {
      // Option A: query the session temp table immediately
      await using var detail = new NpgsqlCommand(
          "SELECT referentialid FROM dms.temp_reference_stage WHERE aliasid IS NULL",
          connection,
          transaction);
      await using var reader = await detail.ExecuteReaderAsync();
      // ... collect GUIDs and raise application error
  }

  (If you prefer a temp table per session, keep ON COMMIT PRESERVE ROWS; if you want it scoped to a single transaction use ON COMMIT DELETE ROWS and fetch the failures before commit.)

  ———

  4. Optional enhancements

  1. Functional variant for invalid IDs – create dms.FetchInvalidReferences() that reads failures from the staging table or a logging table keyed on (parent_document_id,
     parent_partition_key, txid_current()).
  2. Prepared statements – call command.Prepare() after the first execution per connection to lock in the plan; the function now has stable parameter types, so reuse works well.
  3. Batch inserts – for very large payloads, populate temp_reference_stage via COPY using NpgsqlBinaryImporter before calling the function to avoid transmitting long arrays.
  4. Auto-vacuum relief – once the ON CONFLICT path is live, monitor n_dead_tup on reference_* partitions; with fewer deletes the autovacuum frequency can be dialed back (raise
     autovacuum_vacuum_scale_factor per partition if necessary).

  This ON CONFLICT approach keeps the algorithm “insert-or-update + delete what’s gone,” removing the extra update statement and shaving per-call WAL while still protecting referential
  integrity. Let me know when you’re ready to benchmark it—we can drop it into the performance harness and compare wal_bytes and latency against the current function.
