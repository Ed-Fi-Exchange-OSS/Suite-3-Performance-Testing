-- SPDX-License-Identifier: Apache-2.0
-- Licensed to the Ed-Fi Alliance under one or more agreements.
-- The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
-- See the LICENSE and NOTICES files in the project root for more information.

-- Upserts document references for a parent document using one SQL statement that drives
-- staging, validation, upsert, delete, and return logic purely through CTEs.
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
    result RECORD;
BEGIN
    WITH staged AS MATERIALIZED (
             -- Expand the parallel arrays once, resolving aliases/documents so every downstream
             -- step can reuse the same in-memory rows without hitting dms.Alias repeatedly.
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
         invalid AS (
             -- Invalid referential Ids are the ones that failed to resolve to an alias row.
             SELECT COALESCE(array_agg(DISTINCT referentialid), ARRAY[]::uuid[]) AS invalid_ids
             FROM staged
             WHERE aliasid IS NULL
         ),
         duplicates AS (
             SELECT EXISTS (
                        SELECT 1
                        FROM staged
                        GROUP BY referentialpartitionkey, referentialid
                        HAVING COUNT(*) > 1
                    ) AS has_duplicates
         ),
         diffs AS (
             SELECT EXISTS (
                        SELECT 1
                        FROM staged s
                        CROSS JOIN invalid i
                        CROSS JOIN duplicates d
                        LEFT JOIN dms.Reference r
                               ON r.ParentDocumentPartitionKey = s.parentdocumentpartitionkey
                              AND r.ParentDocumentId = s.parentdocumentid
                              AND r.AliasId = s.aliasid
                        WHERE cardinality(i.invalid_ids) = 0
                          AND NOT p_isPureInsert
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
             SELECT EXISTS (
                        SELECT 1
                        FROM dms.Reference r
                        CROSS JOIN invalid i
                        CROSS JOIN duplicates d
                        WHERE cardinality(i.invalid_ids) = 0
                          AND NOT p_isPureInsert
                          AND NOT d.has_duplicates
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
                    ) AS has_orphans
         ),
         write_decision AS (
             -- Decide whether the subsequent DML should run; prevents unnecessary I/O and keeps
             -- the DML branches simple.
             SELECT
                 cardinality(i.invalid_ids) = 0 AS no_invalids,
                 d.has_duplicates,
                 CASE
                     WHEN cardinality(i.invalid_ids) > 0 OR d.has_duplicates THEN FALSE
                     WHEN p_isPureInsert THEN TRUE
                     ELSE (df.has_difference OR orph.has_orphans)
                 END AS perform_upsert,
                 CASE
                     WHEN cardinality(i.invalid_ids) > 0 OR d.has_duplicates THEN FALSE
                     ELSE (NOT p_isPureInsert) AND (df.has_difference OR orph.has_orphans)
                 END AS perform_delete
             FROM invalid i
             CROSS JOIN duplicates d
             CROSS JOIN diffs df
             CROSS JOIN orphans orph
         ),
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
         deleted AS (
             DELETE FROM dms.Reference AS r
             USING write_decision wd
             WHERE wd.perform_delete
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
             RETURNING 1
         )
    SELECT
        wd.no_invalids AS success,
        i.invalid_ids,
        wd.has_duplicates
    INTO result
    FROM invalid i
    CROSS JOIN write_decision wd
    LEFT JOIN LATERAL (SELECT 1 FROM upsert LIMIT 1) up ON TRUE
    LEFT JOIN LATERAL (SELECT 1 FROM deleted LIMIT 1) del ON TRUE;

    IF result.has_duplicates THEN
        RAISE EXCEPTION
            USING MESSAGE = 'InsertReferences: duplicate referentialIds are not allowed.',
                  ERRCODE = '23505';
    END IF;

    RETURN QUERY
    SELECT
        result.success,
        result.invalid_ids;
END;
$$;
