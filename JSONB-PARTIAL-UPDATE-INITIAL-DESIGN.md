Here is a design document based on our conversation, detailing the problem of inefficient JSONB updates in PostgreSQL and the "Diff-and-Patch" solution we developed.

-----

## Design Doc: Efficient JSONB Partial Updates in PostgreSQL

### 1\. Problem Statement

Updating large `JSONB` columns in PostgreSQL by sending a full new document (e.g., `UPDATE ... SET data = @new_data`) is highly inefficient. This "full replacement" method forces PostgreSQL to write the *entire* new JSONB object to its TOAST table and generate a corresponding large entry in the Write-Ahead Log (WAL).

This behavior leads to:

  * **High WAL Generation:** Causes significant I/O, disk space pressure, and bloat.
  * **Performance Bottlenecks:** Slows down `UPDATE` transactions and can impact replication.
  * **Inefficient Network Traffic:** The application must send the full JSON document, even for a minimal change.

The goal is to implement a "surgical" update process that only applies the differences between the old and new JSON documents, thus minimizing WAL writes and network I/O.

-----

### 2\. Proposed Solution: The "Diff-and-Patch" Pattern

We will implement a two-part solution that generates a patch of changes in the application layer and applies that patch in the database layer.

1.  **Application Layer (C\#):** The C\# application will be responsible for calculating the difference ("diff") between the current document and the new document.

      * It will **read** the current JSONB from the database.
      * It will **compare** it to the new JSON document provided by the business logic.
      * It will **generate** a standard **JSON Patch (RFC 6902)** document that describes the changes (e.g., `[{ "op": "replace", "path": "/name", "value": "New" }]`).
      * It will **send only this small patch** to the database, not the full document.

2.  **Database Layer (PostgreSQL):** A custom `plpgsql` function will be created in the database.

      * This function will accept the target `JSONB` column and the JSON Patch document.
      * It will iterate through the patch operations and use efficient, built-in PostgreSQL functions (**`jsonb_set`**, **`jsonb_insert`**, and the **`#-`** operator) to apply each change individually.

This approach ensures that only the modified fragments of the JSONB are written to the TOAST table, resulting in minimal WAL generation.

-----

### 3\. Detailed Implementation

#### 3.1. Application Layer (C\#)

This layer requires a NuGet package to handle the JSON diff operation.

  * **NuGet Package:** `SystemTextJson.JsonDiffPatch`
  * **Command:** `dotnet add package SystemTextJson.JsonDiffPatch`

**Example C\# Code:**

This code demonstrates how to generate the patch document.

```csharp
using System.Text.Json;
using System.Text.Json.Nodes;
using SystemTextJson.JsonDiffPatch;

public class JsonUpdateService
{
    public string GeneratePatch(string oldJson, string newJson)
    {
        // Parse the old and new JSON strings into JsonNode
        var oldNode = JsonNode.Parse(oldJson);
        var newNode = JsonNode.Parse(newJson);

        // Generate the JSON Patch document
        var patch = oldNode.Diff(newNode);

        if (patch is null)
        {
            // The documents are identical
            return null;
        }

        // Serialize the patch to send to Postgres
        return JsonSerializer.Serialize(patch);
    }

    // Your data access code will then call the database
    // with this patch string.
    public async Task UpdateDocument(int id, string patchDocument)
    {
        var sql = @"
            UPDATE my_table
            SET data = jsonb_patch(data, @patch::jsonb)
            WHERE id = @id";

        // Example using Dapper
        // await connection.ExecuteAsync(sql,
        //    new { patch = patchDocument, id = id });
    }
}
```

#### 3.2. Database Layer (PostgreSQL)

This `plpgsql` function must be created in the database one time. It is designed to correctly apply the JSON Patch, crucially distinguishing between `jsonb_set` (for object/replace) and `jsonb_insert` (for array insertions).

**SQL Function Definition:**

```sql
CREATE OR REPLACE FUNCTION jsonb_patch(
    target JSONB,
    patch JSONB
)
RETURNS JSONB
LANGUAGE plpgsql
AS $$
DECLARE
    patch_element JSONB;
    op TEXT;
    path_parts TEXT[];
    parent_path TEXT[];
    parent_element JSONB;
    value JSONB;
    last_part TEXT;
    append_index INT;
BEGIN
    IF jsonb_typeof(patch) != 'array' THEN
        RAISE EXCEPTION 'Patch must be a JSON array';
    END IF;

    FOR patch_element IN SELECT * FROM jsonb_array_elements(patch)
    LOOP
        op := patch_element->>'op';
        path_parts := (
            SELECT array_agg(part)
            FROM jsonb_array_elements_text(patch_element->'path') AS part
        );

        -- 'value' is used by add, replace
        IF patch_element ? 'value' THEN
             value := patch_element->'value';
        END IF;

        CASE op
            WHEN 'replace' THEN
                -- 'replace' ALWAYS overwrites. jsonb_set is correct.
                target := jsonb_set(target, path_parts, value, TRUE);

            WHEN 'remove' THEN
                target := target #- path_parts;

            WHEN 'add' THEN
                -- 'add' is complex. We must check if the parent is an array.
                parent_path := path_parts[1:array_length(path_parts, 1) - 1];

                IF array_length(parent_path, 1) = 0 THEN
                    parent_element := target; -- Parent is the root
                ELSE
                    parent_element := target #> parent_path;
                END IF;

                last_part := path_parts[array_length(path_parts, 1)];

                -- If parent is an array, we MUST use jsonb_insert
                IF jsonb_typeof(parent_element) = 'array' THEN

                    -- Check for the special 'append' syntax (e.g., /tags/-)
                    IF last_part = '-' THEN
                        append_index := jsonb_array_length(parent_element);
                        path_parts[array_length(path_parts, 1)] := append_index::text;
                    END IF;

                    target := jsonb_insert(target, path_parts, value);
                ELSE
                    -- Parent is an object. For objects, 'add' acts like 'replace'.
                    -- jsonb_set (with create_missing=true) is correct.
                    target := jsonb_set(target, path_parts, value, TRUE);
                END IF;

            ELSE
                RAISE EXCEPTION 'Unsupported patch operation: %', op;
        END CASE;
    END LOOP;

    RETURN target;
END;
$$;
```

-----

### 4\. Example Workflow (End-to-End)

1.  **Initial State:** The database contains a user with `id = 1`:
    `{ "name": "Alice", "level": 10, "tags": ["a", "c"] }`

2.  **Application Request:** A request comes in to update user 1. The new document is:
    `{ "name": "Alice", "level": 11, "tags": ["a", "b", "c"] }`

3.  **Application Logic (C\#):**

      * The application reads the old JSON.
      * The `GeneratePatch` method is called:
          * `oldJson`: `{ "name": "Alice", "level": 10, "tags": ["a", "c"] }`
          * `newJson`: `{ "name": "Alice", "level": 11, "tags": ["a", "b", "c"] }`
      * `SystemTextJson.JsonDiffPatch` generates the following patch:
        ```json
        [
          { "op": "replace", "path": "/level", "value": 11 },
          { "op": "add", "path": "/tags/1", "value": "b" }
        ]
        ```

4.  **Database Execution:**

      * The C\# code calls the `UpdateDocument` method, which executes the following SQL:

    <!-- end list -->

    ```sql
    UPDATE users
    SET profile = jsonb_patch(profile, @patch::jsonb)
    WHERE id = 1;
    ```

      * `@patch` is set to the JSON string from step 3.

5.  **`jsonb_patch` Function:**

      * **Loop 1:** `op: "replace"`, `path: "/level"`. The function executes `jsonb_set` to change `/level` to `11`.
      * **Loop 2:** `op: "add"`, `path: "/tags/1"`. The function checks the parent (`/tags`) and sees it's an array. It correctly executes `jsonb_insert` to add `"b"` at index 1, shifting `"c"` to index 2.

6.  **Final State:** The row is updated. The WAL only contains the minimal changes for the `level` key and the `tags` array insertion.
    `{ "name": "Alice", "level": 11, "tags": ["a", "b", "c"] }`
