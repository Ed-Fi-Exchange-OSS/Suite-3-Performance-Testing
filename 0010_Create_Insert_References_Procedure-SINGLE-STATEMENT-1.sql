-- SPDX-License-Identifier: Apache-2.0
-- Licensed to the Ed-Fi Alliance under one or more agreements.
-- The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
-- See the LICENSE and NOTICES files in the project root for more information.

-- Upserts document references for a parent document using a single MERGE-based statement.
-- The provided referentialIds MUST be unique.
-- Returns a success flag plus the invalid referentialIds if unsuccessful.
--
-- Design notes:
--   * All work (validation, upsert, delete, return) happens inside one SQL statement so every
--     step shares the same snapshot and the staged rows are generated exactly once.
--   * We still target the concrete reference partition to preserve deterministic partition
--     pruning rather than depending on runtime pruning against the root partition.
--   * The MERGE handles inserts, updates, and deletions in one pass; a helper CTE decides when
--     those branches should run so we can short-circuit on invalid or duplicate input.
--   * `merge_stats` is intentionally read even though we don't use the count; the cross join
--     guarantees the MERGE side effects fire before the function returns.
CREATE OR REPLACE FUNCTION dms.InsertReferences(
    p_parentDocumentId BIGINT,
    p_parentDocumentPartitionKey SMALLINT,
    p_referentialIds UUID[],
    p_referentialPartitionKeys SMALLINT[],
    p_isPureInsert BOOLEAN DEFAULT FALSE
) RETURNS TABLE (
    success BOOLEAN,
    invalid_ids UUID[]
)
LANGUAGE plpgsql
AS
$$
DECLARE
    reference_partition TEXT := format('reference_%s', lpad(p_parentDocumentPartitionKey::text, 2, '0'));
    result RECORD;
BEGIN
    EXECUTE format($sql$
        WITH staged AS MATERIALIZED (
            -- Expand the incoming arrays once, resolving aliases so downstream CTEs can
            -- reuse the same staged rows without hitting dms.Alias multiple times.
            SELECT
                $1::bigint AS parentdocumentid,
                $2::smallint AS parentdocumentpartitionkey,
                ids.referentialPartitionKey,
                ids.referentialId,
                a.Id AS aliasid,
                a.DocumentId AS referenceddocumentid,
                a.DocumentPartitionKey AS referenceddocumentpartitionkey
            FROM unnest($3::uuid[], $4::smallint[])
                AS ids(referentialId, referentialPartitionKey)
            LEFT JOIN dms.Alias a
                   ON a.ReferentialId = ids.referentialId
                  AND a.ReferentialPartitionKey = ids.referentialPartitionKey
        ),
        invalid AS (
            -- Capture invalid referential IDs (missing alias rows) once for reuse. Returning
            -- this CTE avoids rebuilding the array and lets later CTEs gate their work.
            SELECT COALESCE(array_agg(DISTINCT referentialid), ARRAY[]::uuid[]) AS invalid_ids
            FROM staged
            WHERE aliasid IS NULL
        ),
        duplicates AS (
            -- Detect caller violations of the "IDs must be unique" contract so we can raise
            -- the same exception the temp-table PK enforced.
            SELECT EXISTS (
                       SELECT 1
                       FROM staged
                       GROUP BY referentialpartitionkey, referentialid
                       HAVING COUNT(*) > 1
                   ) AS has_duplicates
        ),
        diffs AS (
            -- Check for differences between staged data and the existing references in the
            -- exact partition while honoring the invalid/duplicate short circuits.
            SELECT EXISTS (
                       SELECT 1
                       FROM staged s
                       CROSS JOIN invalid i
                       CROSS JOIN duplicates d
                       LEFT JOIN dms.%1$I r
                              ON r.ParentDocumentPartitionKey = s.parentdocumentpartitionkey
                             AND r.ParentDocumentId = s.parentdocumentid
                             AND r.AliasId = s.aliasid
                       WHERE cardinality(i.invalid_ids) = 0
                         AND NOT $5::boolean
                         AND NOT d.has_duplicates
                         AND s.aliasid IS NOT NULL
                         AND (
                                r.AliasId IS NULL
                             OR r.ReferentialPartitionKey IS DISTINCT FROM s.referentialpartitionkey
                             OR r.ReferencedDocumentId IS DISTINCT FROM s.referenceddocumentid
                             OR r.ReferencedDocumentPartitionKey IS DISTINCT FROM s.referenceddocumentpartitionkey
                           )
                   ) AS has_difference
        ),
        orphans AS (
            -- Detect references currently stored for the parent that no longer appear in the
            -- staged set, again short-circuiting when we already know we will not write.
            SELECT EXISTS (
                       SELECT 1
                       FROM dms.%1$I r
                       CROSS JOIN invalid i
                       CROSS JOIN duplicates d
                       WHERE cardinality(i.invalid_ids) = 0
                         AND NOT $5::boolean
                         AND NOT d.has_duplicates
                         AND r.ParentDocumentPartitionKey = $2
                         AND r.ParentDocumentId = $1
                         AND NOT EXISTS (
                                 SELECT 1
                                 FROM staged s
                                 WHERE s.parentdocumentpartitionkey = r.ParentDocumentPartitionKey
                                   AND s.parentdocumentid = r.ParentDocumentId
                                   AND s.aliasid = r.AliasId
                                   AND s.referentialpartitionkey = r.ReferentialPartitionKey
                                   AND s.referenceddocumentid = r.ReferencedDocumentId
                                   AND s.referenceddocumentpartitionkey = r.ReferencedDocumentPartitionKey
                             )
                   ) AS has_orphans
        ),
        write_decision AS (
            -- Centralize the "should we write/delete" logic so MERGE branches stay readable
            -- and we do not repeat predicate trees throughout the statement.
            SELECT
                cardinality(i.invalid_ids) = 0 AS no_invalids,
                d.has_duplicates,
                CASE
                    WHEN cardinality(i.invalid_ids) > 0 OR d.has_duplicates THEN FALSE
                    WHEN $5::boolean THEN TRUE
                    ELSE (df.has_difference OR orph.has_orphans)
                END AS perform_merge,
                CASE
                    WHEN cardinality(i.invalid_ids) > 0 OR d.has_duplicates THEN FALSE
                    ELSE (NOT $5::boolean) AND (df.has_difference OR orph.has_orphans)
                END AS perform_delete
            FROM invalid i
            CROSS JOIN duplicates d
            CROSS JOIN diffs df
            CROSS JOIN orphans orph
        ),
        merge_action AS (
            -- Execute the MERGE against the specific reference partition. Source rows only
            -- exist when we previously decided to write, which keeps MERGE lean and ensures
            -- the ON clauses stay partition-local.
            MERGE INTO dms.%1$I AS target
            USING (
                SELECT
                    s.parentdocumentid,
                    s.parentdocumentpartitionkey,
                    s.aliasid,
                    s.referentialpartitionkey,
                    s.referenceddocumentid,
                    s.referenceddocumentpartitionkey
                FROM staged s
                CROSS JOIN write_decision wd
                WHERE s.aliasid IS NOT NULL
                  AND wd.perform_merge
            ) AS source (
                parentdocumentid,
                parentdocumentpartitionkey,
                aliasid,
                referentialpartitionkey,
                referenceddocumentid,
                referenceddocumentpartitionkey
            )
            ON (
                target.ParentDocumentPartitionKey = source.parentdocumentpartitionkey
                AND target.ParentDocumentId = source.parentdocumentid
                AND target.AliasId = source.aliasid
            )
            WHEN MATCHED AND (
                (SELECT perform_merge FROM write_decision)
                AND (
                       target.ReferentialPartitionKey IS DISTINCT FROM source.referentialpartitionkey
                    OR target.ReferencedDocumentId IS DISTINCT FROM source.referenceddocumentid
                    OR target.ReferencedDocumentPartitionKey IS DISTINCT FROM source.referenceddocumentpartitionkey
                )
            ) THEN
                -- Existing reference row points at a different target document; update it to
                -- match the staged metadata.
                UPDATE
                    SET ReferentialPartitionKey = source.referentialpartitionkey,
                        ReferencedDocumentId = source.referenceddocumentid,
                        ReferencedDocumentPartitionKey = source.referencedDocumentPartitionKey
            WHEN NOT MATCHED AND (SELECT perform_merge FROM write_decision) THEN
                -- No existing reference row for this alias: insert a new one that ties the
                -- parent to the resolved alias/document tuple.
                INSERT (
                    ParentDocumentId,
                    ParentDocumentPartitionKey,
                    AliasId,
                    ReferentialPartitionKey,
                    ReferencedDocumentId,
                    ReferencedDocumentPartitionKey
                )
                VALUES (
                    source.parentdocumentid,
                    source.parentdocumentpartitionkey,
                    source.aliasid,
                    source.referentialpartitionkey,
                    source.referenceddocumentid,
                    source.referencedDocumentPartitionKey
                )
            WHEN NOT MATCHED BY SOURCE AND (
                (SELECT perform_delete FROM write_decision)
                AND target.ParentDocumentPartitionKey = $2
                AND target.ParentDocumentId = $1
            ) THEN
                -- Rows present in Reference but missing from the staged input are orphans; delete
                -- them only when the earlier checks concluded we are syncing the parent.
                DELETE
        ),
        merge_stats AS (
            -- Reading the MERGE output forces PostgreSQL to execute the MERGE before we
            -- fetch the invalid IDs, preserving the intended ordering of side effects.
            SELECT COUNT(*) AS applied_rows
            FROM merge_action
        )
        SELECT
            wd.no_invalids AS success,
            i.invalid_ids,
            wd.has_duplicates
        FROM invalid i
        CROSS JOIN write_decision wd
        CROSS JOIN merge_stats
    $sql$, reference_partition)
    INTO result
    USING p_parentDocumentId,
          p_parentDocumentPartitionKey,
          p_referentialIds,
          p_referentialPartitionKeys,
          p_isPureInsert;

    IF result.has_duplicates THEN
        RAISE EXCEPTION 'InsertReferences: duplicate referentialIds are not allowed.';
    END IF;

    RETURN QUERY
    SELECT
        result.success,
        result.invalid_ids;
END;
$$;
