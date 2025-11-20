-- SPDX-License-Identifier: Apache-2.0
-- Licensed to the Ed-Fi Alliance under one or more agreements.
-- The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
-- See the LICENSE and NOTICES files in the project root for more information.

-- Upserts document references for a parent document by relying on a pair of
-- statements: the first performs staging/validation work only, while the second
-- issues the required DML against the specific partition table. Keeping the
-- staging data in CTEs avoids temp-table churn yet still ensures invalid or
-- duplicate payloads short-circuit without touching the large dms.Reference set.
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
    reference_partition TEXT;
    staged_cte TEXT;
    dml_sql TEXT;
    invalid_uuid_list UUID[] := ARRAY[]::uuid[];
    has_duplicates BOOLEAN := FALSE;
    duplicate_partition SMALLINT;
    duplicate_referential UUID;
    is_pure_literal TEXT;
BEGIN
    reference_partition := format('reference_%s', lpad(p_parentDocumentPartitionKey::text, 2, '0'));

    -- Stage + validation pass: detect invalid referentialIds and duplicate payloads
    -- before touching the large Reference table.
    WITH -- Normalize inputs and join to Alias once for reuse everywhere.
         staged AS MATERIALIZED (
             SELECT
                 p_parentDocumentId AS parentdocumentid,
                 p_parentDocumentPartitionKey AS parentdocumentpartitionkey,
                 ids.referentialPartitionKey,
                 ids.referentialId,
                 a.Id AS aliasid,
                 a.DocumentId AS referenceddocumentid,
                 a.DocumentPartitionKey AS referenceddocumentpartitionkey
             FROM unnest(p_referentialIds, p_referentialPartitionKeys)
                 AS ids(referentialId, referentialPartitionKey)
             LEFT JOIN dms.Alias a
                    ON a.ReferentialId = ids.referentialId
                   AND a.ReferentialPartitionKey = ids.referentialPartitionKey
         ),
         -- Collect unresolved referential IDs up front.
         invalid AS (
             SELECT COALESCE(array_agg(DISTINCT referentialid), ARRAY[]::uuid[]) AS invalid_ids
             FROM staged
             WHERE aliasid IS NULL
         ),
         -- Identify duplicate (partition, UUID) pairs in the payload.
         dup_candidates AS (
             SELECT referentialpartitionkey, referentialid
             FROM staged
             GROUP BY referentialpartitionkey, referentialid
             HAVING COUNT(*) > 1
         ),
         -- Reduce duplicate detection to a boolean + sample pair for errors.
         duplicates AS (
             SELECT
                 EXISTS (SELECT 1 FROM dup_candidates) AS has_duplicates,
                 (SELECT referentialpartitionkey FROM dup_candidates LIMIT 1) AS sample_partition,
                 (SELECT referentialid FROM dup_candidates LIMIT 1) AS sample_id
         )
    SELECT
        i.invalid_ids,
        d.has_duplicates,
        d.sample_partition,
        d.sample_id
    INTO invalid_uuid_list, has_duplicates, duplicate_partition, duplicate_referential
    FROM invalid i
    CROSS JOIN duplicates d;

    -- Preserve existing error contract by re-raising the temp-table-style violation.
    IF has_duplicates THEN
        RAISE EXCEPTION
            USING ERRCODE = '23505',
                  CONSTRAINT = 'reference_stage_pkey',
                  MESSAGE = 'duplicate key value violates unique constraint "reference_stage_pkey"',
                  DETAIL = format(
                      'Key (referentialpartitionkey, referentialid)=(%s,%s) already exists.',
                      duplicate_partition,
                      duplicate_referential
                  );
    END IF;

    -- Invalid referential IDs short-circuit with the original return signature.
    IF cardinality(invalid_uuid_list) > 0 THEN
        RETURN QUERY
        SELECT FALSE, invalid_uuid_list;
        RETURN;
    END IF;

    -- Build the reusable staged CTE as dynamic SQL so we can inject the resolved
    -- reference partition name while still binding all parameters safely.
    staged_cte := '
        WITH staged AS MATERIALIZED (
            SELECT
                $3::bigint AS parentdocumentid,
                $4::smallint AS parentdocumentpartitionkey,
                ids.referentialPartitionKey,
                ids.referentialId,
                a.Id AS aliasid,
                a.DocumentId AS referenceddocumentid,
                a.DocumentPartitionKey AS referenceddocumentpartitionkey
            FROM unnest($1::uuid[], $2::smallint[])
                AS ids(referentialId, referentialPartitionKey)
            LEFT JOIN dms.Alias a
                   ON a.ReferentialId = ids.referentialId
                  AND a.ReferentialPartitionKey = ids.referentialPartitionKey
        )';

    is_pure_literal := CASE WHEN p_isPureInsert THEN 'TRUE' ELSE 'FALSE' END;

    -- The second statement performs diff/orphan detection plus upsert/delete
    -- directly against the concrete partition. CASE guards avoid scanning when
    -- the call is known to be a pure insert.
    dml_sql := format(
        $fmt$
        %s,
        -- Detect whether staged rows differ from existing references.
        diffs AS (
            SELECT CASE
                WHEN %s THEN FALSE
                ELSE EXISTS (
                    SELECT 1
                    FROM staged s
                    LEFT JOIN dms.%I r
                           ON r.ParentDocumentPartitionKey = s.parentdocumentpartitionkey
                          AND r.ParentDocumentId = s.parentdocumentid
                          AND r.AliasId = s.aliasid
                    WHERE s.aliasid IS NOT NULL
                      AND (
                             r.AliasId IS NULL
                          OR r.ReferentialPartitionKey IS DISTINCT FROM s.referentialpartitionkey
                          OR r.ReferencedDocumentId IS DISTINCT FROM s.referenceddocumentid
                          OR r.ReferencedDocumentPartitionKey IS DISTINCT FROM s.referenceddocumentpartitionkey
                      )
                )
            END AS has_difference
        ),
        -- Detect whether existing references would become orphans.
        orphans AS (
            SELECT CASE
                WHEN %s THEN FALSE
                ELSE EXISTS (
                    SELECT 1
                    FROM dms.%I r
                    WHERE r.ParentDocumentPartitionKey = $4
                      AND r.ParentDocumentId = $3
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
                )
            END AS has_orphans
        ),
        -- Centralize skip logic so the DML branches only run when necessary.
        write_decision AS (
            SELECT
                CASE
                    WHEN %s THEN TRUE
                    ELSE (df.has_difference OR orph.has_orphans)
                END AS perform_upsert,
                CASE
                    WHEN %s THEN FALSE
                    ELSE (df.has_difference OR orph.has_orphans)
                END AS perform_delete
            FROM diffs df
            CROSS JOIN orphans orph
        ),
        -- Partition-targeted upsert mirrors original ON CONFLICT logic.
        upsert AS (
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
            CROSS JOIN write_decision wd
            WHERE s.aliasid IS NOT NULL
              AND wd.perform_upsert
            ON CONFLICT ON CONSTRAINT ux_reference_parent_alias
            DO UPDATE
               SET ReferentialPartitionKey = EXCLUDED.ReferentialPartitionKey,
                   ReferencedDocumentId = EXCLUDED.ReferencedDocumentId,
                   ReferencedDocumentPartitionKey = EXCLUDED.ReferencedDocumentPartitionKey
            WHERE (
                      target.ReferentialPartitionKey,
                      target.ReferencedDocumentId,
                      target.ReferencedDocumentPartitionKey
                  ) IS DISTINCT FROM (
                      EXCLUDED.ReferentialPartitionKey,
                      EXCLUDED.ReferencedDocumentId,
                      EXCLUDED.ReferencedDocumentPartitionKey
                  )
            RETURNING 1
        ),
        -- Partition-targeted delete removes orphaned references when allowed.
        deleted AS (
            DELETE FROM dms.%I AS r
            USING write_decision wd
            WHERE wd.perform_delete
              AND r.ParentDocumentPartitionKey = $4
              AND r.ParentDocumentId = $3
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
            RETURNING 1
        )
        SELECT 1;
        $fmt$,
        staged_cte,
        is_pure_literal,
        reference_partition,
        is_pure_literal,
        reference_partition,
        is_pure_literal,
        is_pure_literal,
        reference_partition
    );

    EXECUTE dml_sql
        USING p_referentialIds, p_referentialPartitionKeys, p_parentDocumentId, p_parentDocumentPartitionKey;

    -- Reuse the previously buffered invalid list; success flag is always TRUE
    -- here because duplicates/invalids never reach this point.
    RETURN QUERY
    SELECT TRUE, invalid_uuid_list;
END;
$$;
