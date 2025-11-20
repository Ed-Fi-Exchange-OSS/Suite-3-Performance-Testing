-- SPDX-License-Identifier: Apache-2.0
-- Licensed to the Ed-Fi Alliance under one or more agreements.
-- The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
-- See the LICENSE and NOTICES files in the project root for more information.

-- Upserts document references for a parent document entirely within a single
-- statement. A materialized CTE stages the payload, performs validation, and
-- feeds the partition-scoped DML so we avoid temp-table churn while keeping a
-- single READ COMMITTED snapshot for the whole operation.
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
    has_null_input BOOLEAN := FALSE;
    null_partition SMALLINT;
    null_referential UUID;
    null_column TEXT;
BEGIN
    reference_partition := format('reference_%s', lpad(p_parentDocumentPartitionKey::text, 2, '0'));

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

    -- Single statement performs payload validation plus diff/orphan detection and
    -- only executes the DML branches when the payload is valid.
    dml_sql := format(
        $fmt$
        %s,
        invalid AS (
            SELECT COALESCE(array_agg(DISTINCT referentialid), ARRAY[]::uuid[]) AS invalid_ids
            FROM staged
            WHERE aliasid IS NULL
        ),
        dup_candidates AS (
            SELECT referentialpartitionkey, referentialid
            FROM staged
            GROUP BY referentialpartitionkey, referentialid
            HAVING COUNT(*) > 1
        ),
        duplicates AS (
            SELECT
                EXISTS (SELECT 1 FROM dup_candidates) AS has_duplicates,
                (SELECT referentialpartitionkey FROM dup_candidates LIMIT 1) AS sample_partition,
                (SELECT referentialid FROM dup_candidates LIMIT 1) AS sample_id
        ),
        null_payload AS (
            SELECT
                EXISTS (
                    SELECT 1
                    FROM staged
                    WHERE referentialid IS NULL OR referentialpartitionkey IS NULL
                ) AS has_nulls,
                (SELECT referentialpartitionkey FROM staged WHERE referentialid IS NULL OR referentialpartitionkey IS NULL LIMIT 1) AS null_partition,
                (SELECT referentialid FROM staged WHERE referentialid IS NULL OR referentialpartitionkey IS NULL LIMIT 1) AS null_id,
                (SELECT CASE
                        WHEN referentialid IS NULL THEN 'referentialid'
                        ELSE 'referentialpartitionkey'
                    END
                 FROM staged
                 WHERE referentialid IS NULL OR referentialpartitionkey IS NULL
                 LIMIT 1) AS null_column
        ),
        payload_status AS (
            SELECT
                i.invalid_ids,
                cardinality(i.invalid_ids) > 0 AS has_invalid,
                d.has_duplicates,
                d.sample_partition,
                d.sample_id,
                np.has_nulls,
                np.null_partition,
                np.null_id,
                np.null_column
            FROM invalid i
            CROSS JOIN duplicates d
            CROSS JOIN null_payload np
        ),
        -- Detect whether staged rows differ from existing references.
        diffs AS (
            SELECT CASE
                WHEN ps.has_invalid OR ps.has_duplicates OR ps.has_nulls OR %s THEN FALSE
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
            FROM payload_status ps
        ),
        -- Detect whether existing references would become orphans.
        orphans AS (
            SELECT CASE
                WHEN ps.has_invalid OR ps.has_duplicates OR ps.has_nulls OR %s THEN FALSE
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
            FROM payload_status ps
        ),
        -- Centralize skip logic so the DML branches only run when necessary.
        write_decision AS (
            SELECT
                CASE
                    WHEN ps.has_invalid OR ps.has_duplicates OR ps.has_nulls THEN FALSE
                    WHEN %s THEN TRUE
                    ELSE (df.has_difference OR orph.has_orphans)
                END AS perform_upsert,
                CASE
                    WHEN ps.has_invalid OR ps.has_duplicates OR ps.has_nulls THEN FALSE
                    WHEN %s THEN FALSE
                    ELSE (df.has_difference OR orph.has_orphans)
                END AS perform_delete
            FROM payload_status ps
            CROSS JOIN diffs df
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
        ),
        results AS (
            SELECT
                ps.invalid_ids,
                ps.has_duplicates,
                ps.sample_partition,
                ps.sample_id,
                ps.has_nulls,
                ps.null_partition,
                ps.null_id,
                ps.null_column
            FROM payload_status ps
        )
        SELECT * FROM results;
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
        USING p_referentialIds, p_referentialPartitionKeys, p_parentDocumentId, p_parentDocumentPartitionKey
        INTO invalid_uuid_list, has_duplicates, duplicate_partition, duplicate_referential,
             has_null_input, null_partition, null_referential, null_column;

    invalid_uuid_list := COALESCE(invalid_uuid_list, ARRAY[]::uuid[]);

    IF has_null_input THEN
        RAISE EXCEPTION
            USING ERRCODE = '23502',
                  MESSAGE = format(
                      'null value in column "%s" of relation "reference_stage" violates not-null constraint',
                      COALESCE(null_column, 'referentialid')
                  ),
                  DETAIL = format(
                      'Failing row contains (%s, %s, %s, %s, %s, %s, %s).',
                      p_parentDocumentId,
                      p_parentDocumentPartitionKey,
                      COALESCE(null_partition::text, 'null'),
                      COALESCE(null_referential::text, 'null'),
                      'null',
                      'null',
                      'null'
                  );
    END IF;

    IF has_duplicates THEN
        RAISE EXCEPTION
            USING ERRCODE = '23505',
                  CONSTRAINT = 'reference_stage_pkey',
                  MESSAGE = 'duplicate key value violates unique constraint "reference_stage_pkey"',
                  DETAIL = format(
                      'Key (referentialpartitionkey, referentialid)=(%s, %s) already exists.',
                      duplicate_partition,
                      duplicate_referential
                  );
    END IF;

    IF cardinality(invalid_uuid_list) > 0 THEN
        RETURN QUERY
        SELECT FALSE, invalid_uuid_list;
        RETURN;
    END IF;

    RETURN QUERY
    SELECT TRUE, invalid_uuid_list;
END;
$$;
