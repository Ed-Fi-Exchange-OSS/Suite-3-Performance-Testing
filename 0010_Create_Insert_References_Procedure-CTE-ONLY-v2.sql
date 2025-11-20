-- SPDX-License-Identifier: Apache-2.0
-- Licensed to the Ed-Fi Alliance under one or more agreements.
-- The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
-- See the LICENSE and NOTICES files in the project root for more information.

-- Upserts document references for a parent document using static CTE staging only (no temp table).
-- The provided referentialIds MUST be unique.
-- Returns a success flag plus the invalid referentialIds if unsuccessful.
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
    has_duplicates BOOLEAN := FALSE;
    needs_upsert BOOLEAN := TRUE;
    stage_has_difference BOOLEAN := FALSE;
    reference_has_orphans BOOLEAN := FALSE;
BEGIN
    -- First pass: build staged data once, detect invalid IDs, duplicates,
    -- and (when not a pure insert) whether there are any changes or orphans.
    WITH staged AS MATERIALIZED (
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
         duplicates AS (
             SELECT 1
             FROM staged
             GROUP BY referentialpartitionkey, referentialid
             HAVING COUNT(*) > 1
         ),
         invalid AS (
             SELECT COALESCE(array_agg(DISTINCT referentialid), ARRAY[]::uuid[]) AS invalid_ids
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
             WHERE NOT p_isPureInsert
               AND s.aliasid IS NOT NULL
               AND (
                      r.AliasId IS NULL
                   OR r.ReferentialPartitionKey IS DISTINCT FROM s.referentialpartitionkey
                   OR r.ReferencedDocumentId IS DISTINCT FROM s.referenceddocumentid
                   OR r.ReferencedDocumentPartitionKey IS DISTINCT FROM s.referenceddocumentpartitionkey
               )
             LIMIT 1
         ),
         orphans AS (
             SELECT 1
             FROM dms.Reference r
             WHERE NOT p_isPureInsert
               AND r.ParentDocumentPartitionKey = p_parentDocumentPartitionKey
               AND r.ParentDocumentId = p_parentDocumentId
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
             LIMIT 1
         )
    SELECT
        i.invalid_ids,
        EXISTS (SELECT 1 FROM duplicates),
        EXISTS (SELECT 1 FROM diffs),
        EXISTS (SELECT 1 FROM orphans)
    INTO invalid_ids, has_duplicates, stage_has_difference, reference_has_orphans
    FROM invalid AS i;

    -- Enforce the uniqueness contract on the incoming referential IDs.
    IF has_duplicates THEN
        RAISE EXCEPTION 'InsertReferences: duplicate referentialIds are not allowed.';
    END IF;

    IF cardinality(invalid_ids) = 0 THEN
        -- Optimization: detect when staged references exactly mirror existing references
        -- for this parent document (no changes and no orphans), so we can skip the write path.
        IF NOT p_isPureInsert THEN
            IF NOT stage_has_difference AND NOT reference_has_orphans THEN
                needs_upsert := FALSE;
            END IF;
        END IF;

        IF needs_upsert THEN
            -- Upsert references directly from the staged CTE, referencing the partitioned
            -- root table so partition pruning can select the appropriate partition.
            WITH staged AS MATERIALIZED (
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
                  );

            -- If this is not a pure insert, remove obsolete references for this parent document.
            IF NOT p_isPureInsert THEN
                WITH staged AS MATERIALIZED (
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
                     )
                DELETE FROM dms.Reference AS r
                WHERE r.ParentDocumentPartitionKey = p_parentDocumentPartitionKey
                  AND r.ParentDocumentId = p_parentDocumentId
                  AND NOT EXISTS (
                          SELECT 1
                          FROM staged s
                          WHERE s.parentdocumentpartitionkey = r.ParentDocumentPartitionKey
                            AND s.parentdocumentid = r.ParentDocumentId
                            AND s.aliasid = r.AliasId
                            AND s.referentialpartitionkey = r.ReferentialPartitionKey
                            AND s.referenceddocumentid = r.ReferencedDocumentId
                            AND s.referenceddocumentpartitionkey = r.ReferencedDocumentPartitionKey
                      );
            END IF;
        END IF;
    END IF;

    RETURN QUERY
    SELECT
        cardinality(invalid_ids) = 0,
        invalid_ids;
END;
$$;

