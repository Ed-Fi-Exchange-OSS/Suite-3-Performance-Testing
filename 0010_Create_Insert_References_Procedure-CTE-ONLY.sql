-- SPDX-License-Identifier: Apache-2.0
-- Licensed to the Ed-Fi Alliance under one or more agreements.
-- The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
-- See the LICENSE and NOTICES files in the project root for more information.

-- Upserts document references for a parent document using CTE staging only (no temp table).
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
    needs_upsert BOOLEAN := TRUE;
    stage_has_difference BOOLEAN := FALSE;
    reference_has_orphans BOOLEAN := FALSE;
    staged_cte_sql CONSTANT TEXT := $staged$
WITH staged AS (
    SELECT $1::BIGINT AS parentdocumentid,
           $2::SMALLINT AS parentdocumentpartitionkey,
           ids.referentialpartitionkey,
           ids.referentialid,
           a.Id AS aliasid,
           a.DocumentId AS referenceddocumentid,
           a.DocumentPartitionKey AS referenceddocumentpartitionkey
    FROM unnest($3::UUID[], $4::SMALLINT[]) AS ids(referentialId, referentialPartitionKey)
    LEFT JOIN dms.Alias a
           ON a.ReferentialId = ids.referentialId
          AND a.ReferentialPartitionKey = ids.referentialPartitionKey
)
$staged$;
BEGIN
    reference_partition := format('reference_%s', lpad(p_parentDocumentPartitionKey::text, 2, '0'));

    -- Detect invalid referential identifiers (no alias rows).
    EXECUTE staged_cte_sql || '
        SELECT COALESCE(array_agg(DISTINCT referentialid), ARRAY[]::uuid[])
        FROM staged
        WHERE aliasid IS NULL
    '
    INTO invalid_ids
    USING p_parentDocumentId, p_parentDocumentPartitionKey, p_referentialIds, p_referentialPartitionKeys;

    IF cardinality(invalid_ids) = 0 THEN
        IF NOT p_isPureInsert THEN
            EXECUTE format('%s
                SELECT EXISTS (
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
                )',
                staged_cte_sql,
                reference_partition)
            INTO stage_has_difference
            USING p_parentDocumentId, p_parentDocumentPartitionKey, p_referentialIds, p_referentialPartitionKeys;

            IF NOT stage_has_difference THEN
                EXECUTE format('%s
                    SELECT EXISTS (
                        SELECT 1
                        FROM dms.%I r
                        WHERE r.ParentDocumentPartitionKey = $2
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
                    )',
                    staged_cte_sql,
                    reference_partition)
                INTO reference_has_orphans
                USING p_parentDocumentId, p_parentDocumentPartitionKey, p_referentialIds, p_referentialPartitionKeys;

                IF NOT reference_has_orphans THEN
                    needs_upsert := FALSE;
                END IF;
            END IF;
        END IF;

        IF needs_upsert THEN
            -- Upsert references directly from the staged CTE.
            EXECUTE staged_cte_sql || '
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
            '
            USING p_parentDocumentId, p_parentDocumentPartitionKey, p_referentialIds, p_referentialPartitionKeys;

            IF NOT p_isPureInsert THEN
                -- Remove orphans using the per-partition table and staged data.
                EXECUTE format('%s
                    DELETE FROM %I.%I AS r
                    WHERE r.ParentDocumentPartitionKey = $2
                      AND r.ParentDocumentId = $1
                      AND NOT EXISTS (
                          SELECT 1
                          FROM staged s
                          WHERE s.parentdocumentpartitionkey = $2
                            AND s.parentdocumentid = $1
                            AND s.aliasid = r.aliasid
                            AND s.referentialpartitionkey = r.referentialpartitionkey
                            AND s.referenceddocumentid = r.referenceddocumentid
                            AND s.referenceddocumentpartitionkey = r.ReferencedDocumentPartitionKey
                      )',
                    staged_cte_sql,
                    'dms',
                    reference_partition)
                USING p_parentDocumentId, p_parentDocumentPartitionKey, p_referentialIds, p_referentialPartitionKeys;
            END IF;
        END IF;
    END IF;

    RETURN QUERY
    SELECT
        cardinality(invalid_ids) = 0,
        invalid_ids;
END;
$$;
