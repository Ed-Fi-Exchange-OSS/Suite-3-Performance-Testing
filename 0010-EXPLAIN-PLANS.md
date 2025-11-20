 Below are concrete EXPLAIN (ANALYZE, BUFFERS) patterns you can run to validate the v2 function’s behavior and plans. I’ll focus on:

  - How to drive realistic inputs.
  - How to EXPLAIN the three core phases: analysis, upsert, delete.
  - What to look for in the plans.

  I’ll use placeholders like $parentId, $pk, $ids, $pks, $isPureInsert that you’ll substitute with real values or psql variables.

  ———

  1. Prepare realistic test inputs

  Pick a parent and a reference set that actually exist:

  - Choose a partition key pk (0–15) and a parent document in that partition:

    SELECT documentpartitionkey, id
    FROM dms.Document
    WHERE documentpartitionkey = 3
    LIMIT 1;
    -- Use: pk = 3, parentId = that Id
  - Build a “typical” batch of referential IDs for that parent size (e.g., ~20 rows) from dms.Alias:

    SELECT array_agg(referentialid)   AS ids,
           array_agg(referentialpartitionkey) AS pks
    FROM dms.Alias
    WHERE referentialpartitionkey = 3
    LIMIT 20;

  Use the resulting arrays in the EXPLAINs below.

  ———

  2. EXPLAIN the “analysis” phase (invalids + diffs + orphans)

  This mirrors the first big WITH in v2, using a single static statement:

  EXPLAIN (ANALYZE, BUFFERS, VERBOSE)
  WITH staged AS MATERIALIZED (
         SELECT
             $parentId::bigint   AS parentdocumentid,
             $pk::smallint       AS parentdocumentpartitionkey,
             ids.referentialpartitionkey,
             ids.referentialid,
             a.id                AS aliasid,
             a.documentid        AS referenceddocumentid,
             a.documentpartitionkey AS referenceddocumentpartitionkey
         FROM unnest($ids::uuid[], $pks::smallint[])
              AS ids(referentialid, referentialpartitionkey)
         LEFT JOIN dms.Alias a
                ON a.ReferentialId = ids.referentialId
               AND a.ReferentialPartitionKey = ids.ReferentialPartitionKey
       ),
       invalid AS (
         SELECT coalesce(array_agg(DISTINCT referentialid), '{}'::uuid[]) AS invalid_ids
         FROM staged
         WHERE aliasid IS NULL
       ),
       diffs AS (
         SELECT 1
         FROM staged s
         LEFT JOIN dms.Reference r
                ON r.ParentDocumentPartitionKey = s.parentdocumentpartitionkey
               AND r.ParentDocumentId = s.parentdocumentid
               AND r.AliasId = s.aliasid
         WHERE NOT $isPureInsert
           AND s.aliasid IS NOT NULL
           AND (
                  r.AliasId IS NULL
               OR r.ReferentialPartitionKey IS DISTINCT FROM s.referentialpartitionkey
               OR r.ReferencedDocumentId  IS DISTINCT FROM s.referenceddocumentid
               OR r.ReferencedDocumentPartitionKey IS DISTINCT FROM s.referenceddocumentpartitionkey
           )
         LIMIT 1
       ),
       orphans AS (
         SELECT 1
         FROM dms.Reference r
         WHERE NOT $isPureInsert
           AND r.ParentDocumentPartitionKey = $pk
           AND r.ParentDocumentId = $parentId
           AND NOT EXISTS (
                 SELECT 1
                 FROM staged s
                 WHERE s.parentdocumentpartitionkey = r.ParentDocumentPartitionKey
                   AND s.parentdocumentid          = r.ParentDocumentId
                   AND s.aliasid                   = r.AliasId
                   AND s.referentialpartitionkey   = r.ReferentialPartitionKey
                   AND s.referenceddocumentid      = r.ReferencedDocumentId
                   AND s.referenceddocumentpartitionkey = r.ReferencedDocumentPartitionKey
             )
         LIMIT 1
       )
  SELECT *
  FROM invalid,
       (SELECT EXISTS (SELECT 1 FROM diffs))   AS has_diff,
       (SELECT EXISTS (SELECT 1 FROM orphans)) AS has_orphans;

  What to look for:

  - For staged:
      - CTE Scan on staged with Actual Rows ≈ number of entries in $ids.
      - Nested Loop or Index Scan on the dms.Alias partition only (pruned to one partition by ReferentialPartitionKey).
  - For diffs / orphans:
      - Access only one dms.Reference partition (pruned on ParentDocumentPartitionKey = $pk).
      - Use of IX_Reference_ParentDocumentId and/or ux_reference_parent_alias for the parent/alias lookups.
  - Buffers:
      - Mostly shared hit (hot cache) for Alias/Reference partitions, minimal read or dirtied pages for this SELECT-only phase.

  ———

  3. EXPLAIN the upsert

  This mirrors the WITH staged … INSERT INTO dms.Reference … ON CONFLICT block:

  EXPLAIN (ANALYZE, BUFFERS, VERBOSE)
  WITH staged AS MATERIALIZED (
         SELECT
             $parentId::bigint   AS parentdocumentid,
             $pk::smallint       AS parentdocumentpartitionkey,
             ids.referentialpartitionkey,
             ids.referentialid,
             a.id                AS aliasid,
             a.documentid        AS referenceddocumentid,
             a.documentpartitionkey AS referenceddocumentpartitionkey
         FROM unnest($ids::uuid[], $pks::smallint[])
              AS ids(referentialid, referentialpartitionkey)
         LEFT JOIN dms.Alias a
                ON a.ReferentialId = ids.referentialId
               AND a.ReferentialPartitionKey = ids.ReferentialPartitionKey
       )
  INSERT INTO dms.Reference AS target (
      ParentDocumentId,
      ParentDocumentPartitionKey,
      AliasId,
      ReferentialPartitionKey,
      ReferencedDocumentId,
      ReferencedDocumentPartitionKey
  )
  SELECT
      s.parentdocumentid,
      s.parentdocumentpartitionkey,
      s.aliasid,
      s.referentialpartitionkey,
      s.referenceddocumentid,
      s.referenceddocumentpartitionkey
  FROM staged s
  WHERE s.aliasid IS NOT NULL
  ON CONFLICT ON CONSTRAINT ux_reference_parent_alias
  DO UPDATE
     SET ReferentialPartitionKey       = EXCLUDED.ReferentialPartitionKey,
         ReferencedDocumentId          = EXCLUDED.ReferencedDocumentId,
         ReferencedDocumentPartitionKey= EXCLUDED.ReferencedDocumentPartitionKey
  WHERE (target.ReferentialPartitionKey,
         target.ReferencedDocumentId,
         target.ReferencedDocumentPartitionKey)
     IS DISTINCT FROM
        (EXCLUDED.ReferentialPartitionKey,
         EXCLUDED.ReferencedDocumentId,
         EXCLUDED.ReferencedDocumentPartitionKey);

  Run this twice:

  - Once with a parent that has no references yet (pure insert behavior).
  - Once immediately again with identical $ids/$pks (no-op upsert path).

  What to look for:

  - Insert on dms.Reference with an ON CONFLICT node:
      - Use of the ux_reference_parent_alias index for conflict detection.
      - Partition pruning to the single ParentDocumentPartitionKey = $pk partition.
  - Rows:
      - First run: Actual Rows inserted ≈ number of valid referential IDs.
      - Second run: Actual Rows updated ≈ 0 (because of the WHERE target <> excluded guard).
  - Buffers:
      - Number of shared read/dirtied pages on the reference partition per call; this is your direct write-path cost.

  ———

  4. EXPLAIN the orphan delete

  This mirrors the WITH staged … DELETE FROM dms.Reference … NOT EXISTS (staged) block:

  EXPLAIN (ANALYZE, BUFFERS, VERBOSE)
  WITH staged AS MATERIALIZED (
         SELECT
             $parentId::bigint   AS parentdocumentid,
             $pk::smallint       AS parentdocumentpartitionkey,
             ids.referentialpartitionkey,
             ids.referentialid,
             a.id                AS aliasid,
             a.documentid        AS referenceddocumentid,
             a.documentpartitionkey AS referenceddocumentpartitionkey
         FROM unnest($ids::uuid[], $pks::smallint[])
              AS ids(referentialid, referentialpartitionkey)
         LEFT JOIN dms.Alias a
                ON a.ReferentialId = ids.referentialId
               AND a.ReferentialPartitionKey = ids.ReferentialPartitionKey
       )
  DELETE FROM dms.Reference AS r
  WHERE r.ParentDocumentPartitionKey = $pk
    AND r.ParentDocumentId           = $parentId
    AND NOT EXISTS (
          SELECT 1
          FROM staged s
          WHERE s.parentdocumentpartitionkey   = r.ParentDocumentPartitionKey
            AND s.parentdocumentid            = r.ParentDocumentId
            AND s.aliasid                     = r.AliasId
            AND s.referentialpartitionkey     = r.ReferentialPartitionKey
            AND s.referenceddocumentid        = r.ReferencedDocumentId
            AND s.referenceddocumentpartitionkey = r.ReferencedDocumentPartitionKey
        );

  Test with:

  - A case where you’ve just removed some referential IDs compared to what’s currently in dms.Reference → expect some deletions.
  - A case where no references were removed → expect 0 deletions.

  What to look for:

  - Partition pruning:
      - Only the single ParentDocumentPartitionKey = $pk partition should appear in the plan.
  - Access pattern:
      - Index usage on IX_Reference_ParentDocumentId (or equivalent) for scanning that parent’s rows.
      - For each candidate row, the NOT EXISTS (staged) typically implemented as nested loop + CTE Scan on staged.
  - Buffers:
      - How many pages in the reference partition get read/updated to delete orphans per call.
      - For “no orphans” cases, you want to see minimal work after the index-guided scan.

  ———

  5. Function-level EXPLAIN

  To see the overall cost in one place (including plpgsql function overhead), you can also run:

  EXPLAIN (ANALYZE, BUFFERS, VERBOSE)
  SELECT *
  FROM dms.InsertReferences(
    p_parentDocumentId          := $parentId,
    p_parentDocumentPartitionKey:= $pk,
    p_referentialIds            := $ids,
    p_referentialPartitionKeys  := $pks,
    p_isPureInsert              := false  -- or true
  );

  This won’t show each internal statement’s plan in detail, but:

  - It gives you the total runtime, buffer usage, and row counts for the function call.
  - You can compare this directly to the temp-table version and your current CTE-only v1 under the same inputs.

  ———

  If you share a sample of the actual EXPLAIN (ANALYZE, BUFFERS) output for one of these cases (even just the high-level node list), I can help interpret whether it’s hitting the single
  partitions and indexes as intended or if there’s any obvious mis-planning to fix.
